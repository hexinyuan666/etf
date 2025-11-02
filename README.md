ETF每日评级系统
https://img.shields.io/badge/Python-3.7+-blue.svg
https://img.shields.io/badge/License-MIT-green.svg
https://img.shields.io/badge/ETF-%E8%AF%84%E7%BA%A7%E7%B3%BB%E7%BB%9F-orange.svg

📊 项目简介
这是一个为ETF精英挑战赛开发的智能ETF评级系统（为比赛选择etf做参考），基于多因子量化模型对全市场400+只ETF进行综合评分和排名。系统采用动量、波动率、风险调整收益和趋势质量四大类因子，为投资者提供科学的ETF投资决策支持。

🚀 主要功能
🎯 核心特性
全市场覆盖: 支持400+只ETF的全面分析

多因子模型: 四大类因子综合评分体系

智能排名: 基于量化模型的自动评级排序

投资建议: 提供具体的调仓和挂单建议

分类输出: 结果自动分类保存到不同文件夹

📈 评级因子
动量因子 (权重35%)

1个月动量 (40%)

3个月动量 (30%)

6个月动量 (30%)

趋势斜率

波动率因子 (权重20%)

年化波动率

风险调整收益 (权重25%)

年化夏普比率

趋势质量 (权重20%)

ADX指标 (60%)

200日均线过滤器 (40%)

🛠️ 安装和使用
环境要求
Python 3.7+

依赖包见 requirements.txt

快速开始
克隆项目

bash
git clone https://github.com/hexinyuan666/etf.git
cd etf
安装依赖

bash
pip install -r requirements.txt
运行系统

bash
python etf_daily_rating_complete.py
依赖包
txt
pandas>=1.5.0
numpy>=1.21.0
requests>=2.28.0
yfinance>=0.2.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
schedule>=1.1.0
python-dotenv>=0.19.0
loguru>=0.6.0
tqdm>=4.64.0
ta>=0.11.0
scipy>=1.13.1  
📁 项目结构
text
etf-rating-system/
├── etf_daily_rating_complete.py  # 主程序文件
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
├── complete_ratings/             # 完整评级结果文件夹
│   └── etf_complete_rating_YYYYMMDD_HHMM.csv
├── top100_ratings/               # 前100名结果文件夹
│   └── etf_top100_rating_YYYYMMDD_HHMM.csv
└── etf_holdings.json            # 持仓记录文件
📊 输出文件
系统会自动生成两类输出文件：

1. 完整评级文件 (complete_ratings/)
包含所有有效ETF的完整排名

包含所有技术指标和因子得分

文件命名: etf_complete_rating_YYYYMMDD_HHMM.csv

2. 前100名文件 (top100_ratings/)
仅包含综合得分前100名的ETF

便于快速查看优质ETF

文件命名: etf_top100_rating_YYYYMMDD_HHMM.csv

🎯 使用示例
运行结果展示
text
🚀 启动完整版ETF每日评级系统...
📁 输出文件夹已创建:
   - 完整评级: complete_ratings/
   - 前100名: top100_ratings/
📋 使用完整ETF列表...
📊 ETF总数: 400+
🎯 开始生成完整ETF评级排名...
⏳ 进度: 0/400 (0.0%) - 成功: 0 - 预计剩余: 45.2分钟
...
✅ 数据处理完成! 有效ETF数量: 350/400
⏱️ 总耗时: 25.3分钟

🎯 ETF完整综合评级排名
🏆 ETF综合排名 (前50):
排名 代码          名称                 当前价   涨跌幅  综合得分    动量     波动率   夏普     趋势质量  
1    159509.SZ    纳指科技ETF          2.345    +1.25%   2.345     0.123   0.045   1.234     0.567
2    159994.SZ    5GETF               1.678    +0.89%   2.123     0.098   0.032   1.156     0.489
...

💡 推荐持仓 (前3名):
1. 纳指科技ETF (159509.SZ) - 得分: 2.345
2. 5GETF (159994.SZ) - 得分: 2.123
3. 电池50ETF (159796.SZ) - 得分: 2.098

💰 挂单价格建议 (基于ATR波动率):
📈 纳指科技ETF:
   当前价: 2.345
   建议买入区间: 2.245 - 2.305
   保守买入价: 2.275
   建议仓位: 33.3% (等权重)
🔧 自定义配置
在 CompleteETFDailyRating 类中，您可以调整以下参数：

python
# 因子权重
self.weight_momentum = 0.35
self.weight_volatility = 0.20
self.weight_risk_adjusted = 0.25
self.weight_trend_quality = 0.20

# 显示数量
self.top_n = 50      # 显示前50名
self.recommend_n = 3 # 推荐前3名
📈 策略优势
科学量化: 基于历史数据的多因子模型

全面覆盖: 全市场ETF分析，不漏掉任何机会

实时更新: 每日自动获取最新数据

风险控制: 综合考虑波动率和夏普比率

趋势跟踪: ADX和均线系统识别强势品种

🤝 贡献指南
欢迎为这个项目贡献代码！请遵循以下步骤：

Fork 本项目

创建特性分支 (git checkout -b feature/AmazingFeature)

提交更改 (git commit -m 'Add some AmazingFeature')

推送到分支 (git push origin feature/AmazingFeature)

开启一个 Pull Request

📄 许可证
本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情

⚠️ 风险提示
本系统仅为投资参考工具，不构成投资建议

过往表现不代表未来收益

投资有风险，入市需谨慎

📞 联系我们
如有问题或建议，请通过以下方式联系：

GitHub Issues: 项目Issues页面

邮箱: 2099394435@qq.com
