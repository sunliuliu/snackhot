"""全局速率控制器 + 分源限速 + 指数退避 + 失败熔断

核心理念：稳字当头。宁可慢，不要触发风控。

用法：
    limiter = RateLimiter()          # 全局单例
    await limiter.wait("weibo")      # 请求前 await，自动按节奏等够
    limiter.record_success("weibo")  # 成功调用
    limiter.record_failure("weibo")  # 失败调用（触发退避/熔断）
"""
import asyncio, time, random, json
from pathlib import Path
from datetime import date
from config import (
    SOURCE_RATES, DEFAULT_RATE, GLOBAL_MIN_INTERVAL,
    DAILY_TOTAL_LIMIT, FAILURE_COOLDOWN, FAILURE_THRESHOLD,
)


class RateLimiter:
    """全局速率控制器（asyncio 友好，单例模式）"""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._last_global_ts = 0.0          # 上一次任意请求的时间戳
        self._source_states = {}            # {name: {"last_ts": float, "failures": int, "cooldown_until": float}}
        self._today = date.today().isoformat()
        self._daily_count = 0
        # 从文件恢复状态（防止程序重启丢失统计）
        self._state_file = Path(__file__).parent.parent / "_cache" / "rate_state.json"
        self._load_state()

    def _load_state(self):
        try:
            if self._state_file.exists():
                st = json.loads(self._state_file.read_text())
                if st.get("date") == self._today:
                    self._daily_count = st.get("count", 0)
        except:
            pass

    def _save_state(self):
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            self._state_file.write_text(json.dumps({
                "date": self._today,
                "count": self._daily_count,
            }))
        except:
            pass

    # ---------- 核心等待 ----------
    async def wait(self, source_name: str):
        """在发起请求前调用，自动等待够节奏"""

        # 1) 每日总量检查
        today = date.today().isoformat()
        if today != self._today:
            self._today = today
            self._daily_count = 0

        if self._daily_count >= DAILY_TOTAL_LIMIT:
            # 超了，等 1 分钟再检查
            print(f"  ⏳ 今日总请求已达 {DAILY_TOTAL_LIMIT}，冷却中...", flush=True)
            await asyncio.sleep(60)
            return await self.wait(source_name)  # 递归重试

        # 2) 获取/初始化 source 状态
        if source_name not in self._source_states:
            self._source_states[source_name] = {
                "last_ts": 0.0,
                "failures": 0,
                "cooldown_until": 0.0,
                "backoff": 1.0,
            }
        state = self._source_states[source_name]

        # 3) 熔断检查
        if state["cooldown_until"] > time.time():
            remain = state["cooldown_until"] - time.time()
            print(f"  ⚠️  {source_name} 熔断中，剩余 {remain:.0f}s，跳过本轮", flush=True)
            await asyncio.sleep(min(remain, 10))
            return  # 上层 fetch 会因等太久返回空

        # 4) 速率表查询
        min_intv, max_intv, _daily_max = SOURCE_RATES.get(source_name, DEFAULT_RATE)

        # 指数退避叠加（失败多了间隔翻倍）
        effective_min = min_intv * state["backoff"]
        effective_max = max_intv * state["backoff"]

        # 5) 分源等待
        now = time.time()
        elapsed = now - state["last_ts"]
        source_wait = random.uniform(effective_min, effective_max) - elapsed
        if source_wait > 0:
            await asyncio.sleep(source_wait)

        # 6) 全局等待
        now = time.time()
        global_wait = GLOBAL_MIN_INTERVAL - (now - self._last_global_ts)
        if global_wait > 0:
            await asyncio.sleep(global_wait)

        # 7) 记录
        state["last_ts"] = time.time()
        self._last_global_ts = state["last_ts"]
        self._daily_count += 1
        self._save_state()

    # ---------- 成功/失败反馈 ----------
    def record_success(self, source_name: str):
        if source_name in self._source_states:
            self._source_states[source_name]["failures"] = 0
            self._source_states[source_name]["backoff"] = 1.0

    def record_failure(self, source_name: str):
        if source_name not in self._source_states:
            self._source_states[source_name] = {"last_ts": 0, "failures": 0, "cooldown_until": 0, "backoff": 1.0}
        st = self._source_states[source_name]
        st["failures"] += 1
        # 指数退避：每次失败 backoff × 1.5
        st["backoff"] = min(st["backoff"] * 1.5, 10.0)

        if st["failures"] >= FAILURE_THRESHOLD:
            cooldown = FAILURE_COOLDOWN * (2 ** (st["failures"] - FAILURE_THRESHOLD))
            cooldown = min(cooldown, 600)  # 最长冷却 10 分钟
            st["cooldown_until"] = time.time() + cooldown
            print(f"  🔥 {source_name} 连续 {st['failures']} 次失败，熔断 {cooldown:.0f}s", flush=True)

    # ---------- 状态查询 ----------
    def status(self) -> str:
        lines = [f"全局: 今日 {self._daily_count}/{DAILY_TOTAL_LIMIT}"]
        for name, st in self._source_states.items():
            lines.append(f"  {name}: backoff={st['backoff']:.1f}× failures={st['failures']} cooldown={max(0, st['cooldown_until']-time.time()):.0f}s")
        return "\n".join(lines)