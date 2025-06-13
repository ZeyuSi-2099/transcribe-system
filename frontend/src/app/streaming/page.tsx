import StreamingConverter from '@/components/StreamingConverter';

export default function StreamingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* 页面标题 */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
              ⚡ 流式转换测试
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
              体验实时转换功能，观看AI逐步生成转换结果的完整过程
            </p>
          </div>

          {/* 功能特色说明 */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border">
              <div className="text-blue-600 dark:text-blue-400 font-semibold mb-2">
                🔄 实时转换
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-300">
                无需等待，实时看到转换进度和结果生成
              </div>
            </div>
            
            <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border">
              <div className="text-green-600 dark:text-green-400 font-semibold mb-2">
                📊 进度可视化
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-300">
                清晰的进度条和状态提示，转换过程一目了然
              </div>
            </div>
            
            <div className="bg-white dark:bg-slate-800 p-4 rounded-lg border">
              <div className="text-purple-600 dark:text-purple-400 font-semibold mb-2">
                🎯 智能识别
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-300">
                自动识别对话类型，应用最优转换策略
              </div>
            </div>
          </div>

          {/* 流式转换组件 */}
          <StreamingConverter />

          {/* 测试示例 */}
          <div className="mt-8 bg-white dark:bg-slate-800 p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-white">
              💡 测试示例
            </h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-medium text-slate-700 dark:text-slate-300 mb-2">
                  面试对话示例：
                </h4>
                <div className="bg-slate-50 dark:bg-slate-700 p-3 rounded border text-slate-600 dark:text-slate-300">
                  面试官: 请介绍一下你的工作经验。<br/>
                  我: 我有三年的软件开发经验，主要负责后端开发。<br/>
                  面试官: 具体用过哪些技术？<br/>
                  我: 主要是Python和JavaScript。
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-slate-700 dark:text-slate-300 mb-2">
                  日常对话示例：
                </h4>
                <div className="bg-slate-50 dark:bg-slate-700 p-3 rounded border text-slate-600 dark:text-slate-300">
                  朋友: 今天天气真不错。<br/>
                  我: 是啊，很适合出去走走。<br/>
                  朋友: 要不要一起去公园？<br/>
                  我: 好主意，我们下午去吧。
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 