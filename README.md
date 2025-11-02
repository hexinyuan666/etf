# ETF 每日评级系统

一个为参加“ETF 菁英挑战赛”设计的多因子 ETF 量化评级系统。系统对全市场 400+ 只 ETF（以沪深和部分跨境标的为主）进行日常打分与排序，帮助快速筛选优质标的并给出挂单与调仓建议。

## 🎯 项目亮点

- 多因子评分：动量、波动率、风险调整收益与趋势质量四大因子加权组合（可复现并可调权重）
- 全市场覆盖：支持 400+ 只 ETF 的批量分析
- 智能推荐：自动产出前 3 名推荐持仓
- 挂单建议：基于 ATR 提供合理的买入区间与保守挂单价
- 调仓建议：提供持仓管理与风险控制要点

## ✨ 核心策略（默认权重）

- 动量因子 35% — 包含 1 个月 / 3 个月 / 6 个月动量及趋势斜率
- 波动率因子 20% — 年化波动率（越低越优）
- 风险调整收益 25% — 夏普比率
- 趋势质量 20% — ADX 指标与 200 日均线过滤

因子支持截面 Z-score 标准化与去极值处理（winsorize），并按权重合成最终综合得分。

## 📊 输出内容

- 综合排名：默认显示前 50 名，CSV 文件保存至 `complete_ratings/`
- 类别排名：按宽基 / 行业 / 跨境 / 商品等展示各类别内的优质标的
- 推荐持仓：前 3 名标的与建议仓位（等权）
- 挂单建议：基于 ATR 的买入区间与保守挂单价
- 调仓策略：优先配置、等权分配、逢高减仓等操作建议

## 🛠 快速开始

推荐在虚拟环境中运行。下面给出 PowerShell 与 Bash 两种常用命令示例：

PowerShell (Windows):

```powershell
cd E:\project\etf
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python etf_dailyrating_v1.1.py
```

Bash (Linux / WSL / macOS):

```bash
cd /path/to/project/etf
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python etf_dailyrating_v1.1.py
```

说明：项目中有两份脚本：`etf_dailyrating_v1.py`（基础版）和 `etf_dailyrating_v1.1.py`（完整版）。完整版会产出更完整的因子与挂单建议。

## ⚙️ 文件说明

- `etf_dailyrating_v1.1.py` — 完整版主程序（含因子计算、排名、挂单建议、保存输出）
- `etf_dailyrating_v1.py` — 基础版主程序（简化版）
- `requirements.txt` — Python 依赖
- `etf_holdings.json` — 可选的持仓记录（运行时读写）
- `complete_ratings/` — 完整排名 CSV 存放目录
- `top100_ratings/` — 前 100 名 CSV 存放目录

输出示例文件名：
- `etf_complete_rating_YYYYMMDD_HHMM.csv`
- `etf_top100_rating_YYYYMMDD_HHMM.csv`

## 因子细则（简述）

| 因子类别 | 权重 | 指标 |
|---|---:|---|
| 动量 | 35% | 1 个月 / 3 个月 / 6 个月动量、趋势斜率 |
| 波动率 | 20% | 年化波动率 |
| 风险调整收益 | 25% | 夏普比率 |
| 趋势质量 | 20% | ADX 指标、200 日均线过滤 |

注：波动率取负值后参与截面标准化（越低越优），夏普与趋势质量为正向因子。

## ⚠️ 风险提示

本系统为量化研究工具，仅用于策略开发与数据分析，不构成投资建议。市场有风险，投资需谨慎。请在真实资金投入前做充分回测与风险管理。

## 📄 许可证

本项目使用 MIT 许可证（详见仓库根目录 `LICENSE`）。如需更改授权信息，请在 `LICENSE` 中替换版权声明。

## 开发与扩展建议

- 可选：并发/异步抓取数据以提升速度（注意限流与重试机制）
- 将输出生成 HTML 报告或接入自动通知（邮件 / 企业微信）
- 添加单元测试与 GitHub Actions 做持续集成

## 联系与支持

如需帮助，请提供：Python 版本、完整错误日志和你运行的脚本名字（例如 `etf_dailyrating_v1.1.py`），我会协助定位与修复问题。
邮箱：2099394435@qq.com
