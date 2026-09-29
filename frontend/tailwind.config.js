/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', '"PingFang SC"', '"Microsoft YaHei"', 'system-ui', 'sans-serif'],
        display: ['"Playfair Display"', '"Noto Serif SC"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', '"SF Mono"', 'Menlo', 'monospace'],
      },
      colors: {
        // === 主色系：温暖零食橙 ===
        brand: {
          50:  '#FFF8F0',
          100: '#FFECD9',
          200: '#FFD4A8',
          300: '#FFB872',
          400: '#FF9940',
          500: '#F97316',   // 主品牌橙
          600: '#EA580C',
          700: '#C2410C',
        },
        // === 墨色（主文字） ===
        ink: {
          900: '#1C1917',   // 标题
          800: '#292524',   // 主文字
          700: '#44403C',   // 次文字
          500: '#78716C',   // meta 文字
          400: '#A8A29E',   // 辅助
          300: '#D6D3D1',   // 线框
          200: '#E7E5E4',   // 分割
          100: '#F5F5F4',   // chip
        },
        // === 背景 ===
        bg: {
          page:  '#FAF9F6',   // 暖米色底
          card:  '#FFFFFF',   // 卡片白
          sunk:  '#F9F9F6',   // 下沉块
          muted: '#F5F5F4',   // 辅助底
        },
        // === 状态色 ===
        state: {
          rise:   '#DC2626',   // 涨（红）
          fall:   '#16A34A',   // 跌（绿）
          hot:    '#EA580C',   // 热
          info:   '#0891B2',   // 信息
          warn:   '#CA8A04',   // 提醒
          success:'#16A34A',
        },
        // === 分类色（按 event_type 自动映射） ===
        cat: {
          earnings:   '#EA580C',   // 财报 — 橙红
          channel:    '#0891B2',   // 渠道 — 青
          product:    '#16A34A',   // 新品 — 绿
          safety:     '#DC2626',   // 安全 — 红
          supply:     '#7C3AED',   // 供应链 — 紫
          collab:     '#DB2777',   // 联名 — 粉
          marketing:  '#F59E0B',   // 营销 — 金
          policy:     '#1E40AF',   // 政策 — 深蓝
        },
      },
      boxShadow: {
        soft:   '0 1px 2px rgba(28,25,23,0.04), 0 4px 12px rgba(28,25,23,0.04)',
        card:   '0 1px 3px rgba(28,25,23,0.06), 0 8px 24px rgba(28,25,23,0.06)',
        hover:  '0 4px 8px rgba(28,25,23,0.08), 0 16px 40px rgba(28,25,23,0.10)',
        ring:   '0 0 0 1px rgba(28,25,23,0.06)',
      },
      borderRadius: {
        card:   '12px',
        chip:   '999px',
      },
      maxWidth: { site: '880px' },
      animation: {
        'fade-in':    'fadeIn 0.3s ease-out',
        'slide-up':   'slideUp 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        'shimmer':    'shimmer 1.4s infinite',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn:    { '0%':{opacity:'0'}, '100%':{opacity:'1'} },
        slideUp:   { '0%':{opacity:'0', transform:'translateY(12px)'}, '100%':{opacity:'1', transform:'translateY(0)'} },
        shimmer:   { '0%':{backgroundPosition:'-400px 0'}, '100%':{backgroundPosition:'400px 0'} },
        pulseSoft: { '0%,100%':{opacity:'1'}, '50%':{opacity:'0.6'} },
      },
    },
  },
  plugins: [],
}