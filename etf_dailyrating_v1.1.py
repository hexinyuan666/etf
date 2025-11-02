# etf_daily_rating_complete.py
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import time
import random
from datetime import datetime, timedelta
from scipy import stats
from scipy.stats import linregress
from scipy.stats.mstats import winsorize
import ta

class CompleteETFDailyRating:
    def __init__(self):
        """
        初始化完整版ETF每日评级系统
        """
        # 因子权重配置（保持与原策略一致）
        self.weight_momentum = 0.35
        self.weight_volatility = 0.20
        self.weight_risk_adjusted = 0.25
        self.weight_trend_quality = 0.20
        
        # 动量因子内部权重
        self.weight_mom_1m = 0.4
        self.weight_mom_3m = 0.3
        self.weight_mom_6m = 0.3
        
        # 趋势质量因子内部权重
        self.weight_adx = 0.6
        self.weight_ma200 = 0.4
        
        # 选股数量
        self.top_n = 50  # 显示前50名
        self.recommend_n = 3
        
        # 数据参数
        self.max_days = 250
        self.min_required_days = 60
        
        # 存储当前持仓
        self.holdings_file = 'etf_holdings.json'
        self.current_holdings = self.load_holdings()
        
        # 创建输出文件夹
        self.setup_output_folders()
    
    def setup_output_folders(self):
        """创建输出文件夹"""
        # 完整评级文件夹
        self.complete_ratings_folder = 'complete_ratings'
        # 前100名文件夹
        self.top100_ratings_folder = 'top100_ratings'
        
        # 创建文件夹（如果不存在）
        os.makedirs(self.complete_ratings_folder, exist_ok=True)
        os.makedirs(self.top100_ratings_folder, exist_ok=True)
        
        print(f"📁 输出文件夹已创建:")
        print(f"   - 完整评级: {self.complete_ratings_folder}/")
        print(f"   - 前100名: {self.top100_ratings_folder}/")
    
    def load_holdings(self):
        """加载当前持仓"""
        if os.path.exists(self.holdings_file):
            with open(self.holdings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_holdings(self, holdings):
        """保存持仓到文件"""
        with open(self.holdings_file, 'w', encoding='utf-8') as f:
            json.dump(holdings, f, ensure_ascii=False, indent=2)
    
    def get_all_etf_list(self):
        """
        获取全市场ETF列表 - 使用完整的备用列表
        """
        print("📋 使用完整ETF列表...")
        return self.get_complete_etf_list()
    
    def get_complete_etf_list(self):
        """
        完整的ETF列表 - 包含所有提供的ETF
        """
        complete_etfs = [
            
            {'ts_code': '159994.SZ', 'name': '5GETF'},
            {'ts_code': '159509.SZ', 'name': '纳指科技ETF'},
            {'ts_code': '159796.SZ', 'name': '电池50ETF'},
            {'ts_code': '159583.SZ', 'name': '通信设备ETF'},
            {'ts_code': '159783.SZ', 'name': '科创创业50ETF'},
            {'ts_code': '159781.SZ', 'name': '科创创业ETF'},
            {'ts_code': '159603.SZ', 'name': '双创龙头ETF'},
            {'ts_code': '159811.SZ', 'name': '5G50ETF'},
            {'ts_code': '159780.SZ', 'name': '双创ETF'},
            {'ts_code': '159782.SZ', 'name': '双创50ETF'},
            {'ts_code': '159368.SZ', 'name': '创业板新能源ETF华夏'},
            {'ts_code': '159383.SZ', 'name': '创业板50ETF华泰柏瑞'},
            {'ts_code': '159566.SZ', 'name': '储能电池ETF'},
            {'ts_code': '159305.SZ', 'name': '储能电池ETF广发'},
            {'ts_code': '159773.SZ', 'name': '创业板科技ETF'},
            {'ts_code': '159652.SZ', 'name': '有色50ETF'},
            {'ts_code': '159375.SZ', 'name': '创业板50ETF国泰'},
            {'ts_code': '159370.SZ', 'name': '创50ETF工银'},
            {'ts_code': '159777.SZ', 'name': '创科技ETF'},
            {'ts_code': '159373.SZ', 'name': '创业板50ETF嘉实'},
            {'ts_code': '159681.SZ', 'name': '创50ETF'},
            {'ts_code': '159779.SZ', 'name': '消费电子50ETF'},
            {'ts_code': '159371.SZ', 'name': '创业板50ETF富国'},
            {'ts_code': '159682.SZ', 'name': '创业50ETF'},
            {'ts_code': '159949.SZ', 'name': '创业板50ETF'},
            {'ts_code': '159752.SZ', 'name': '新能源龙头ETF'},
            {'ts_code': '159597.SZ', 'name': '创业板成长ETF易方达'},
            {'ts_code': '159320.SZ', 'name': '电网ETF'},
            {'ts_code': '159880.SZ', 'name': '有色ETF基金'},
            {'ts_code': '159690.SZ', 'name': '矿业ETF'},
            {'ts_code': '159367.SZ', 'name': '创业板50ETF华夏'},
            {'ts_code': '159676.SZ', 'name': '创业板增强ETF富国'},
            {'ts_code': '159881.SZ', 'name': '有色60ETF'},
            {'ts_code': '159814.SZ', 'name': '创业大盘ETF'},
            {'ts_code': '159871.SZ', 'name': '有色金属ETF'},
            {'ts_code': '159675.SZ', 'name': '创业板增强ETF'},
            {'ts_code': '159502.SZ', 'name': '标普生物科技ETF'},
            {'ts_code': '159381.SZ', 'name': '创业板人工智能ETF华夏'},
            {'ts_code': '159507.SZ', 'name': '通信ETF广发'},
            {'ts_code': '159363.SZ', 'name': '创业板人工智能ETF华宝'},
            {'ts_code': '159991.SZ', 'name': '创大盘ETF'},
            {'ts_code': '159755.SZ', 'name': '电池ETF'},
            {'ts_code': '159767.SZ', 'name': '电池龙头ETF'},
            {'ts_code': '159808.SZ', 'name': '创100ETF融通'},
            {'ts_code': '159819.SZ', 'name': '人工智能ETF'},
            {'ts_code': '159909.SZ', 'name': 'TMT50ETF'},
            {'ts_code': '159757.SZ', 'name': '电池ETF景顺'},
            {'ts_code': '159388.SZ', 'name': '创业板人工智能ETF国泰'},
            {'ts_code': '159840.SZ', 'name': '锂电池ETF'},
            {'ts_code': '159695.SZ', 'name': '通信ETF'},
            {'ts_code': '159906.SZ', 'name': '深成长龙头ETF'},
            {'ts_code': '159958.SZ', 'name': '创业板ETF工银'},
            {'ts_code': '159964.SZ', 'name': '创业板ETF平安'},
            {'ts_code': '159511.SZ', 'name': '通信ETF南方'},
            {'ts_code': '159861.SZ', 'name': '碳中和50ETF'},
            {'ts_code': '159956.SZ', 'name': '创业板ETF建信'},
            {'ts_code': '159875.SZ', 'name': '新能源ETF'},
            {'ts_code': '159824.SZ', 'name': '新能车ETF'},
            {'ts_code': '159821.SZ', 'name': 'BOCI创业板ETF'},
            {'ts_code': '159810.SZ', 'name': '创业板ETF浦银'},
            {'ts_code': '159948.SZ', 'name': '创业板ETF南方'},
            {'ts_code': '159915.SZ', 'name': '创业板ETF'},
            {'ts_code': '159908.SZ', 'name': '创业板ETF博时'},
            {'ts_code': '159709.SZ', 'name': '物联网ETF工银'},
            {'ts_code': '159640.SZ', 'name': '碳中和龙头ETF'},
            {'ts_code': '159885.SZ', 'name': '碳中和ETF基金'},
            {'ts_code': '159957.SZ', 'name': '创业板ETF华夏'},
            {'ts_code': '159896.SZ', 'name': '物联网ETF南方'},
            {'ts_code': '159952.SZ', 'name': '创业板ETF广发'},
            {'ts_code': '159806.SZ', 'name': '新能源车ETF'},
            {'ts_code': '159895.SZ', 'name': '物联网ETF易方达'},
            {'ts_code': '159831.SZ', 'name': '上海金ETF嘉实'},
            {'ts_code': '159671.SZ', 'name': '稀有金属ETF基金'},
            {'ts_code': '159834.SZ', 'name': '金ETF'},
            {'ts_code': '159934.SZ', 'name': '黄金ETF'},
            {'ts_code': '159830.SZ', 'name': '上海金ETF'},
            {'ts_code': '159812.SZ', 'name': '黄金基金ETF'},
            {'ts_code': '159637.SZ', 'name': '新能源车龙头ETF'},
            {'ts_code': '159997.SZ', 'name': '电子ETF'},
            {'ts_code': '159937.SZ', 'name': '黄金ETF基金'},
            {'ts_code': '159790.SZ', 'name': '碳中和ETF'},
            {'ts_code': '159641.SZ', 'name': '双碳ETF'},
            {'ts_code': '159639.SZ', 'name': '碳中和ETF南方'},
            {'ts_code': '159807.SZ', 'name': '科技ETF'},
            {'ts_code': '159602.SZ', 'name': '中国A50ETF'},
            {'ts_code': '159701.SZ', 'name': '物联网ETF招商'},
            {'ts_code': '159716.SZ', 'name': '深证100ETF华宝'},
            {'ts_code': '159642.SZ', 'name': '碳中和100ETF'},
            {'ts_code': '159601.SZ', 'name': 'A50ETF'},
            {'ts_code': '159608.SZ', 'name': '稀有金属ETF'},
            {'ts_code': '159582.SZ', 'name': '半导体产业ETF'},
            {'ts_code': '159501.SZ', 'name': '纳指ETF嘉实'},
            {'ts_code': '159973.SZ', 'name': '民企ETF'},
            {'ts_code': '159941.SZ', 'name': '纳指ETF'},
            {'ts_code': '159944.SZ', 'name': '材料ETF'},
            {'ts_code': '159665.SZ', 'name': '半导体龙头ETF'},
            {'ts_code': '159721.SZ', 'name': '深证100ETF永赢'},
            {'ts_code': '159836.SZ', 'name': '创业板300ETF天弘'},
            {'ts_code': '159660.SZ', 'name': '纳指100ETF'},
            {'ts_code': '159713.SZ', 'name': '稀土ETF'},
            {'ts_code': '159715.SZ', 'name': '稀土ETF易方达'},
            {'ts_code': '159995.SZ', 'name': '芯片ETF'},
            {'ts_code': '159310.SZ', 'name': '芯片ETF天弘'},
            {'ts_code': '159886.SZ', 'name': '机械ETF'},
            {'ts_code': '159599.SZ', 'name': '芯片ETF基金'},
            {'ts_code': '159212.SZ', 'name': '深100ETF南方'},
            {'ts_code': '159738.SZ', 'name': '云计算ETF华泰柏瑞'},
            {'ts_code': '159211.SZ', 'name': '深证100ETF富国'},
            {'ts_code': '159813.SZ', 'name': '半导体ETF'},
            {'ts_code': '159720.SZ', 'name': '智能车ETF泰康'},
            {'ts_code': '159961.SZ', 'name': '深100ETF方正富邦'},
            {'ts_code': '159656.SZ', 'name': '300成长ETF'},
            {'ts_code': '159775.SZ', 'name': '电池ETF基金'},
            {'ts_code': '159912.SZ', 'name': '深300ETF'},
            {'ts_code': '159576.SZ', 'name': '深证100ETF广发'},
            {'ts_code': '159801.SZ', 'name': '芯片ETF龙头'},
            {'ts_code': '159560.SZ', 'name': '芯片ETF景顺'},
            {'ts_code': '159696.SZ', 'name': '纳指ETF易方达'},
            {'ts_code': '159939.SZ', 'name': '信息技术ETF'},
            {'ts_code': '159546.SZ', 'name': '集成电路ETF'},
            {'ts_code': '159325.SZ', 'name': '半导体ETF南方'},
            {'ts_code': '159706.SZ', 'name': '深证100ETF华安'},
            {'ts_code': '159969.SZ', 'name': '深100ETF银华'},
            {'ts_code': '159975.SZ', 'name': '深100ETF招商'},
            {'ts_code': '159150.SZ', 'name': '深证50ETF易方达'},
            {'ts_code': '159632.SZ', 'name': '纳斯达克ETF'},
            {'ts_code': '159513.SZ', 'name': '纳斯达克100指数ETF'},
            {'ts_code': '159659.SZ', 'name': '纳斯达克100ETF'},
            {'ts_code': '159350.SZ', 'name': '深证50ETF富国'},
            {'ts_code': '159763.SZ', 'name': '新材料ETF基金'},
            {'ts_code': '159901.SZ', 'name': '深证100ETF'},
            {'ts_code': '159653.SZ', 'name': 'ESG300ETF'},
            {'ts_code': '159216.SZ', 'name': '深证100ETF大成'},
            {'ts_code': '159631.SZ', 'name': '中证A100ETF'},
            {'ts_code': '159609.SZ', 'name': '光伏龙头ETF'},
            {'ts_code': '159362.SZ', 'name': 'A500ETF工银'},
            {'ts_code': '159553.SZ', 'name': '2000ETF增强'},
            {'ts_code': '159685.SZ', 'name': '1000增强ETF天弘'},
            {'ts_code': '159943.SZ', 'name': '深证成指ETF'},
            {'ts_code': '159380.SZ', 'name': 'A500ETF东财'},
            {'ts_code': '159386.SZ', 'name': 'A500ETF永赢'},
            {'ts_code': '159717.SZ', 'name': 'ESGETF'},
            {'ts_code': '159778.SZ', 'name': '工业互联ETF'},
            {'ts_code': '159703.SZ', 'name': '新材料ETF'},
            {'ts_code': '159970.SZ', 'name': '深100ETF工银'},
            {'ts_code': '159866.SZ', 'name': '日经ETF'},
            {'ts_code': '159627.SZ', 'name': 'A100ETF'},
            {'ts_code': '159215.SZ', 'name': '中证A500ETF指数基金'},
            {'ts_code': '159903.SZ', 'name': '深成ETF'},
            {'ts_code': '159360.SZ', 'name': '中证A500ETF天弘'},
            {'ts_code': '159863.SZ', 'name': '光伏ETF基金'},
            {'ts_code': '159661.SZ', 'name': 'A100ETF嘉实'},
            {'ts_code': '159356.SZ', 'name': 'A500ETF基金'},
            {'ts_code': '159339.SZ', 'name': 'A500ETF'},
            {'ts_code': '159376.SZ', 'name': 'A500ETF指数基金'},
            {'ts_code': '159923.SZ', 'name': '中证A100ETF基金'},
            {'ts_code': '159864.SZ', 'name': '光伏50ETF'},
            {'ts_code': '159351.SZ', 'name': 'A500ETF嘉实'},
            {'ts_code': '159379.SZ', 'name': 'A500ETF融通'},
            {'ts_code': '159678.SZ', 'name': '中证500增强ETF'},
            {'ts_code': '159577.SZ', 'name': '美国50ETF'},
            {'ts_code': '159358.SZ', 'name': '中证A500ETF基金'},
            {'ts_code': '159610.SZ', 'name': '500ETF增强'},
            {'ts_code': '159618.SZ', 'name': '光伏ETF指数基金'},
            {'ts_code': '159761.SZ', 'name': '新材料50ETF'},
            {'ts_code': '159393.SZ', 'name': '沪深300指数ETF'},
            {'ts_code': '159353.SZ', 'name': '中证A500ETF景顺'},
            {'ts_code': '159330.SZ', 'name': '沪深300ETF基金'},
            {'ts_code': '159902.SZ', 'name': '中小100ETF'},
            {'ts_code': '159359.SZ', 'name': '中证A500ETF华安'},
            {'ts_code': '159563.SZ', 'name': '创业板综ETF华夏'},
            {'ts_code': '159686.SZ', 'name': 'A100ETF易方达'},
            {'ts_code': '159630.SZ', 'name': 'A100ETF基金'},
            {'ts_code': '159732.SZ', 'name': '消费电子ETF'},
            {'ts_code': '159673.SZ', 'name': '沪深300ETF鹏华'},
            {'ts_code': '159357.SZ', 'name': '中证A500指数ETF'},
            {'ts_code': '159857.SZ', 'name': '光伏ETF'},
            {'ts_code': '159361.SZ', 'name': 'A500ETF易方达'},
            {'ts_code': '159352.SZ', 'name': 'A500ETF南方'},
            {'ts_code': '159982.SZ', 'name': '中证500ETF鹏华'},
            {'ts_code': '159338.SZ', 'name': '中证A500ETF'},
            {'ts_code': '159326.SZ', 'name': '电网设备ETF'},
            {'ts_code': '159606.SZ', 'name': '中证500成长ETF'},
            {'ts_code': '159562.SZ', 'name': '黄金股ETF'},
            {'ts_code': '159300.SZ', 'name': '300ETF'},
            {'ts_code': '159523.SZ', 'name': '沪深300成长ETF'},
            {'ts_code': '159925.SZ', 'name': '沪深300ETF南方'},
            {'ts_code': '159558.SZ', 'name': '半导体设备ETF易方达'},
            {'ts_code': '159327.SZ', 'name': '半导体设备ETF基金'},
            {'ts_code': '159596.SZ', 'name': 'A50ETF华宝'},
            {'ts_code': '159919.SZ', 'name': '沪深300ETF'},
            {'ts_code': '159315.SZ', 'name': '黄金股ETF基金'},
            {'ts_code': '159968.SZ', 'name': '中证500ETF博时'},
            {'ts_code': '159621.SZ', 'name': 'MSCIESGETF'},
            {'ts_code': '159967.SZ', 'name': '创业板成长ETF'},
            {'ts_code': '159655.SZ', 'name': '标普ETF'},
            {'ts_code': '159516.SZ', 'name': '半导体设备ETF'},
            {'ts_code': '159322.SZ', 'name': '黄金股票ETF基金'},
            {'ts_code': '159623.SZ', 'name': '成渝经济圈ETF'},
            {'ts_code': '159540.SZ', 'name': '信创ETF易方达'},
            {'ts_code': '159791.SZ', 'name': '300ESGETF'},
            {'ts_code': '159800.SZ', 'name': '中证800ETF'},
            {'ts_code': '159820.SZ', 'name': '中证500ETF天弘'},
            {'ts_code': '159935.SZ', 'name': '中证500ETF景顺'},
            {'ts_code': '159922.SZ', 'name': '中证500ETF'},
            {'ts_code': '159966.SZ', 'name': '创业板价值ETF'},
            {'ts_code': '159552.SZ', 'name': '中证2000增强ETF'},
            {'ts_code': '159337.SZ', 'name': '中证500ETF基金'},
            {'ts_code': '159537.SZ', 'name': '信创ETF'},
            {'ts_code': '159658.SZ', 'name': '数字经济ETF'},
            {'ts_code': '159222.SZ', 'name': '自由现金流ETF易方达'},
            {'ts_code': '159538.SZ', 'name': '信创ETF富国'},
            {'ts_code': '159663.SZ', 'name': '机床ETF'},
            {'ts_code': '159541.SZ', 'name': '创业板综ETF万家'},
            {'ts_code': '159201.SZ', 'name': '自由现金流ETF'},
            {'ts_code': '159890.SZ', 'name': '云计算ETF'},
            {'ts_code': '159687.SZ', 'name': '亚太精选ETF'},
            {'ts_code': '159539.SZ', 'name': '信创ETF广发'},
            {'ts_code': '159691.SZ', 'name': '港股红利ETF'},
            {'ts_code': '159667.SZ', 'name': '工业母机ETF'},
            {'ts_code': '159617.SZ', 'name': '500价值ETF'},
            {'ts_code': '159739.SZ', 'name': '大数据ETF'},
            {'ts_code': '159225.SZ', 'name': '现金流ETF基金'},
            {'ts_code': '159565.SZ', 'name': '汽车零部件ETF'},
            {'ts_code': '159591.SZ', 'name': '中证A50ETF'},
            {'ts_code': '159321.SZ', 'name': '黄金股票ETF'},
            {'ts_code': '159588.SZ', 'name': '石油天然气ETF'},
            {'ts_code': '159592.SZ', 'name': 'A50ETF基金'},
            {'ts_code': '159521.SZ', 'name': '国证2000ETF指数基金'},
            {'ts_code': '159543.SZ', 'name': '国证2000ETF基金'},
            {'ts_code': '159390.SZ', 'name': 'A50指数ETF'},
            {'ts_code': '159697.SZ', 'name': '油气ETF'},
            {'ts_code': '159532.SZ', 'name': '中证2000ETF易方达'},
            {'ts_code': '159593.SZ', 'name': '中证A50指数ETF'},
            {'ts_code': '159595.SZ', 'name': '中证A50ETF基金'},
            {'ts_code': '159306.SZ', 'name': '汽车零件ETF'},
            {'ts_code': '159555.SZ', 'name': '2000增强ETF'},
            {'ts_code': '159309.SZ', 'name': '油气资源ETF'},
            {'ts_code': '159976.SZ', 'name': '湾创ETF'},
            {'ts_code': '159527.SZ', 'name': '云计算ETF广发'},
            {'ts_code': '159620.SZ', 'name': '500成长ETF'},
            {'ts_code': '159679.SZ', 'name': '中证1000增强ETF'},
            {'ts_code': '159870.SZ', 'name': '化工ETF'},
            {'ts_code': '159910.SZ', 'name': '基本面120ETF'},
            {'ts_code': '159510.SZ', 'name': '沪深300价值ETF'},
            {'ts_code': '159677.SZ', 'name': '1000增强ETF'},
            {'ts_code': '159519.SZ', 'name': '港股国企ETF'},
            {'ts_code': '159505.SZ', 'name': '国证2000指数ETF'},
            {'ts_code': '159249.SZ', 'name': 'A500增强ETF工银'},
            {'ts_code': '159517.SZ', 'name': '800增强ETF'},
            {'ts_code': '159945.SZ', 'name': '能源ETF广发'},
            {'ts_code': '159930.SZ', 'name': '能源ETF'},
            {'ts_code': '159209.SZ', 'name': '中证红利质量ETF'},
            {'ts_code': '159680.SZ', 'name': '1000ETF增强'},
            {'ts_code': '159723.SZ', 'name': '科技龙头ETF'},
            {'ts_code': '159535.SZ', 'name': '中证2000ETF嘉实'},
            {'ts_code': '159633.SZ', 'name': '中证1000ETF易方达'},
            {'ts_code': '159328.SZ', 'name': '家电ETF易方达'},
            {'ts_code': '159786.SZ', 'name': 'VRETF'},
            {'ts_code': '159731.SZ', 'name': '石化ETF'},
            {'ts_code': '159918.SZ', 'name': '中创400ETF'},
            {'ts_code': '159536.SZ', 'name': '中证2000指数ETF'},
            {'ts_code': '159533.SZ', 'name': '中证2000ETF基金'},
            {'ts_code': '159203.SZ', 'name': '大盘成长ETF'},
            {'ts_code': '159528.SZ', 'name': '国企改革ETF'},
            {'ts_code': '159207.SZ', 'name': '高股息ETF'},
            {'ts_code': '159845.SZ', 'name': '中证1000ETF'},
            {'ts_code': '159399.SZ', 'name': '现金流ETF'},
            {'ts_code': '159629.SZ', 'name': '1000ETF'},
            {'ts_code': '159758.SZ', 'name': '红利质量ETF'},
            {'ts_code': '159980.SZ', 'name': '有色ETF'},
            {'ts_code': '159240.SZ', 'name': '中证A500增强ETF天弘'},
            {'ts_code': '159888.SZ', 'name': '智能车ETF'},
            {'ts_code': '159730.SZ', 'name': '龙头家电ETF'},
            {'ts_code': '159889.SZ', 'name': '智能汽车ETF'},
            {'ts_code': '159805.SZ', 'name': '传媒ETF'},
            {'ts_code': '159611.SZ', 'name': '电力ETF'},
            {'ts_code': '159726.SZ', 'name': '恒生红利ETF'},
            {'ts_code': '159301.SZ', 'name': '公用事业ETF'},
            {'ts_code': '159795.SZ', 'name': '智能汽车ETF基金'},
            {'ts_code': '159226.SZ', 'name': '中证A500增强ETF'},
            {'ts_code': '159236.SZ', 'name': '自由现金流ETF工银'},
            {'ts_code': '159959.SZ', 'name': '央企ETF'},
            {'ts_code': '159238.SZ', 'name': '300ETF增强'},
            {'ts_code': '159531.SZ', 'name': '中证2000ETF'},
            {'ts_code': '159916.SZ', 'name': '深F60ETF'},
            {'ts_code': '159869.SZ', 'name': '游戏ETF'},
            {'ts_code': '159333.SZ', 'name': '港股央企红利ETF'},
            {'ts_code': '159578.SZ', 'name': '深证主板50ETF南方'},
            {'ts_code': '159743.SZ', 'name': '湖北ETF'},
            {'ts_code': '159556.SZ', 'name': '中证2000ETF增强'},
            {'ts_code': '159235.SZ', 'name': '中证现金流ETF'},
            {'ts_code': '159708.SZ', 'name': '红利ETF'},
            {'ts_code': '159996.SZ', 'name': '家电ETF'},
            {'ts_code': '159628.SZ', 'name': '国证2000ETF'},
            {'ts_code': '159219.SZ', 'name': '深证100ETF融通'},
            {'ts_code': '159616.SZ', 'name': '农牧ETF'},
            {'ts_code': '159232.SZ', 'name': '现金流ETF南方'},
            {'ts_code': '159669.SZ', 'name': '绿电ETF'},
            {'ts_code': '159905.SZ', 'name': '深红利ETF'},
            {'ts_code': '159625.SZ', 'name': '绿色电力ETF'},
            {'ts_code': '159804.SZ', 'name': '创中盘88ETF'},
            {'ts_code': '159221.SZ', 'name': '现金流ETF嘉实'},
            {'ts_code': '159233.SZ', 'name': '自由现金流ETF基金'},
            {'ts_code': '159965.SZ', 'name': '央视50ETF'},
            {'ts_code': '159223.SZ', 'name': '现金流ETF永赢'},
            {'ts_code': '159332.SZ', 'name': '央企红利ETF'},
            {'ts_code': '159220.SZ', 'name': '港股通红利ETF'},
            {'ts_code': '159206.SZ', 'name': '卫星ETF'},
            {'ts_code': '159229.SZ', 'name': '自由现金流ETF广发'},
            {'ts_code': '159707.SZ', 'name': '地产ETF'},
            {'ts_code': '159261.SZ', 'name': '创业板新能源ETF鹏华'},
            {'ts_code': '159387.SZ', 'name': '创业板新能源ETF国泰'},
            {'ts_code': '159768.SZ', 'name': '房地产ETF'},
            {'ts_code': '159366.SZ', 'name': '港股医疗ETF'},
            {'ts_code': '159542.SZ', 'name': '工程机械ETF'},
            {'ts_code': '159936.SZ', 'name': '可选消费ETF'},
            {'ts_code': '159698.SZ', 'name': '粮食ETF'},
            {'ts_code': '159205.SZ', 'name': '创业板ETF东财'},
            {'ts_code': '159872.SZ', 'name': '智能网联汽车ETF'},
            {'ts_code': '159581.SZ', 'name': '红利ETF基金'},
            {'ts_code': '159335.SZ', 'name': '央企科创ETF'},
            {'ts_code': '159827.SZ', 'name': '农业50ETF'},
            {'ts_code': '159728.SZ', 'name': '在线消费ETF'},
            {'ts_code': '159551.SZ', 'name': '机器人产业ETF'},
            {'ts_code': '159515.SZ', 'name': '国企红利ETF'},
            {'ts_code': '159793.SZ', 'name': '线上消费ETF基金'},
            {'ts_code': '159526.SZ', 'name': '机器人ETF嘉实'},
            {'ts_code': '159545.SZ', 'name': '恒生红利低波ETF'},
            {'ts_code': '159589.SZ', 'name': '红利ETF广发'},
            {'ts_code': '159372.SZ', 'name': '创业板50ETF万家'},
            {'ts_code': '159770.SZ', 'name': '机器人ETF'},
            {'ts_code': '159587.SZ', 'name': '粮食ETF广发'},
            {'ts_code': '159998.SZ', 'name': '计算机ETF'},
            {'ts_code': '159573.SZ', 'name': '创业板200ETF华夏'},
            {'ts_code': '159619.SZ', 'name': '基建ETF'},
            {'ts_code': '159825.SZ', 'name': '农业ETF'},
            {'ts_code': '159572.SZ', 'name': '创业板200ETF易方达'},
            {'ts_code': '159822.SZ', 'name': '新经济ETF'},
            {'ts_code': '159635.SZ', 'name': '基建50ETF'},
            {'ts_code': '159974.SZ', 'name': '央企创新ETF'},
            {'ts_code': '159788.SZ', 'name': '港股通100ETF'},
            {'ts_code': '159575.SZ', 'name': '创业板200ETF银华'},
            {'ts_code': '159913.SZ', 'name': '深价值ETF'},
            {'ts_code': '159302.SZ', 'name': '港股高股息ETF'},
            {'ts_code': '159712.SZ', 'name': '港股通50ETF'},
            {'ts_code': '159612.SZ', 'name': '标普500ETF'},
            {'ts_code': '159331.SZ', 'name': '红利港股ETF'},
            {'ts_code': '159856.SZ', 'name': '互联网龙头ETF'},
            {'ts_code': '159571.SZ', 'name': '创业板200ETF富国'},
            {'ts_code': '159766.SZ', 'name': '旅游ETF'},
            {'ts_code': '159729.SZ', 'name': '互联网ETF'},
            {'ts_code': '159725.SZ', 'name': '线上消费ETF'},
            {'ts_code': '159385.SZ', 'name': '数字经济ETF富国'},
            {'ts_code': '159549.SZ', 'name': '红利低波ETF天弘'},
            {'ts_code': '159329.SZ', 'name': '沙特ETF'},
            {'ts_code': '159883.SZ', 'name': '医疗器械ETF'},
            {'ts_code': '159311.SZ', 'name': '数字经济ETF易方达'},
            {'ts_code': '159920.SZ', 'name': '恒生ETF'},
            {'ts_code': '159666.SZ', 'name': '交通运输ETF'},
            {'ts_code': '159898.SZ', 'name': '医疗器械指数ETF'},
            {'ts_code': '159742.SZ', 'name': '恒生科技指数ETF'},
            {'ts_code': '159355.SZ', 'name': '800红利低波ETF'},
            {'ts_code': '159797.SZ', 'name': '医疗器械ETF基金'},
            {'ts_code': '159263.SZ', 'name': '价值ETF'},
            {'ts_code': '159662.SZ', 'name': '交运ETF'},
            {'ts_code': '159336.SZ', 'name': '央企红利50ETF'},
            {'ts_code': '159613.SZ', 'name': '信息安全ETF'},
            {'ts_code': '159389.SZ', 'name': '数字经济ETF嘉实'},
            {'ts_code': '159907.SZ', 'name': '2000ETF'},
            {'ts_code': '159312.SZ', 'name': '恒生ETF港股通'},
            {'ts_code': '159993.SZ', 'name': '证券ETF龙头'},
            {'ts_code': '159891.SZ', 'name': '医疗ETF基金'},
            {'ts_code': '159318.SZ', 'name': '恒生港股通ETF'},
            {'ts_code': '159001.SZ', 'name': '货币ETF'},
            {'ts_code': '159719.SZ', 'name': '国企共赢ETF'},
            {'ts_code': '159877.SZ', 'name': '医疗ETF南方'},
            {'ts_code': '159520.SZ', 'name': '消费龙头ETF'},
            {'ts_code': '159848.SZ', 'name': '证券ETF基金'},
            {'ts_code': '159873.SZ', 'name': '医疗设备ETF'},
            {'ts_code': '159842.SZ', 'name': '券商ETF'},
            {'ts_code': '159607.SZ', 'name': '中概互联网ETF'},
            {'ts_code': '159692.SZ', 'name': '证券ETF东财'},
            {'ts_code': '159847.SZ', 'name': '医疗ETF易方达'},
            {'ts_code': '159512.SZ', 'name': '汽车ETF'},
            {'ts_code': '159530.SZ', 'name': '机器人ETF易方达'},
            {'ts_code': '159954.SZ', 'name': 'H股ETF'},
            {'ts_code': '159841.SZ', 'name': '证券ETF'},
            {'ts_code': '159547.SZ', 'name': '红利低波ETF基金'},
            {'ts_code': '159940.SZ', 'name': '金融地产ETF'},
            {'ts_code': '159605.SZ', 'name': '中概互联ETF'},
            {'ts_code': '159929.SZ', 'name': '医药ETF'},
            {'ts_code': '159828.SZ', 'name': '医疗ETF'},
            {'ts_code': '159559.SZ', 'name': '机器人50ETF'},
            {'ts_code': '159838.SZ', 'name': '医药50ETF'},
            {'ts_code': '159855.SZ', 'name': '影视ETF'},
            {'ts_code': '159760.SZ', 'name': '医疗健康ETF泰康'},
            {'ts_code': '159228.SZ', 'name': '红利低波ETF长城'},
            {'ts_code': '159213.SZ', 'name': '机器人ETF基金'},
            {'ts_code': '159850.SZ', 'name': '恒生国企ETF'},
            {'ts_code': '159622.SZ', 'name': '创新药ETF沪港深'},
            {'ts_code': '159938.SZ', 'name': '医药卫生ETF'},
            {'ts_code': '159391.SZ', 'name': '大盘价值ETF'},
            {'ts_code': '159688.SZ', 'name': '恒生互联网ETF'},
            {'ts_code': '159931.SZ', 'name': '金融ETF'},
            {'ts_code': '159202.SZ', 'name': '恒生互联网科技ETF'},
            {'ts_code': '159837.SZ', 'name': '生物科技ETF'},
            {'ts_code': '159303.SZ', 'name': '恒生医疗ETF基金'},
            {'ts_code': '159740.SZ', 'name': '恒生科技ETF'},
            {'ts_code': '159550.SZ', 'name': '互联网ETF沪港深'},
            {'ts_code': '159849.SZ', 'name': '生物科技指数ETF'},
            {'ts_code': '159525.SZ', 'name': '红利低波ETF'},
            {'ts_code': '159859.SZ', 'name': '生物医药ETF'},
            {'ts_code': '159741.SZ', 'name': '恒生科技ETF嘉实'},
            {'ts_code': '159748.SZ', 'name': '创新药ETF富国'},
            {'ts_code': '159365.SZ', 'name': '恒指ETF'},
            {'ts_code': '159776.SZ', 'name': '港股通医药ETF'},
            {'ts_code': '159718.SZ', 'name': '港股医药ETF'},
            {'ts_code': '159839.SZ', 'name': '生物药ETF'},
            {'ts_code': '159858.SZ', 'name': '创新药ETF南方'},
            {'ts_code': '159747.SZ', 'name': '香港科技ETF'},
            {'ts_code': '159657.SZ', 'name': '疫苗ETF鹏华'},
            {'ts_code': '159636.SZ', 'name': '港股通科技30ETF'},
            {'ts_code': '159933.SZ', 'name': '国投金融地产ETF'},
            {'ts_code': '159751.SZ', 'name': '港股科技ETF'},
            {'ts_code': '159382.SZ', 'name': '创业板人工智能ETF南方'},
            {'ts_code': '159323.SZ', 'name': '港股通汽车ETF'},
            {'ts_code': '159246.SZ', 'name': '创业板人工智能ETF富国'},
            {'ts_code': '159508.SZ', 'name': '生物医药ETF基金'},
            {'ts_code': '159670.SZ', 'name': '消费ETF基金'},
            {'ts_code': '159378.SZ', 'name': '通用航空ETF'},
            {'ts_code': '159787.SZ', 'name': '建材ETF易方达'},
            {'ts_code': '159852.SZ', 'name': '软件ETF'},
            {'ts_code': '159557.SZ', 'name': '恒生医疗ETF'},
            {'ts_code': '159899.SZ', 'name': '软件龙头ETF'},
            {'ts_code': '159867.SZ', 'name': '畜牧ETF'},
            {'ts_code': '159992.SZ', 'name': '创新药ETF'},
            {'ts_code': '159835.SZ', 'name': '创新药50ETF'},
            {'ts_code': '159262.SZ', 'name': '港股通科技ETF'},
            {'ts_code': '159798.SZ', 'name': '消费ETF易方达'},
            {'ts_code': '159750.SZ', 'name': '港股科技50ETF'},
            {'ts_code': '159865.SZ', 'name': '养殖ETF'},
            {'ts_code': '159892.SZ', 'name': '恒生医药ETF'},
            {'ts_code': '159643.SZ', 'name': '疫苗ETF'},
            {'ts_code': '159645.SZ', 'name': '疫苗ETF富国'},
            {'ts_code': '159377.SZ', 'name': '创业板医药ETF国泰'},
            {'ts_code': '159745.SZ', 'name': '建材ETF'},
            {'ts_code': '159960.SZ', 'name': '恒生中国企业ETF'},
            {'ts_code': '159590.SZ', 'name': '软件50ETF'},
            {'ts_code': '159647.SZ', 'name': '中药ETF'},
            {'ts_code': '159568.SZ', 'name': '港股互联网ETF'},
            {'ts_code': '159586.SZ', 'name': '计算机ETF南方'},
            {'ts_code': '159239.SZ', 'name': '港股通汽车ETF富国'},
            {'ts_code': '159735.SZ', 'name': '港股消费ETF'},
            {'ts_code': '159561.SZ', 'name': '德国ETF'},
            {'ts_code': '159689.SZ', 'name': '消费ETF南方'},
            {'ts_code': '159615.SZ', 'name': '恒生生物科技ETF'},
            {'ts_code': '159843.SZ', 'name': '食品饮料ETF'},
            {'ts_code': '159736.SZ', 'name': '食品饮料ETF天弘'},
            {'ts_code': '159672.SZ', 'name': '主要消费ETF'},
            {'ts_code': '159928.SZ', 'name': '消费ETF'},
            {'ts_code': '159269.SZ', 'name': '港股通科技ETF南方'},
            {'ts_code': '159792.SZ', 'name': '港股通互联网ETF'},
            {'ts_code': '159638.SZ', 'name': '高端装备ETF'},
            {'ts_code': '159506.SZ', 'name': '港股通医疗ETF富国'},
            {'ts_code': '159237.SZ', 'name': '港股汽车ETF基金'},
            {'ts_code': '159265.SZ', 'name': '港股消费50ETF'},
            {'ts_code': '159518.SZ', 'name': '标普油气ETF'},
            {'ts_code': '159985.SZ', 'name': '豆粕ETF'},
            {'ts_code': '159230.SZ', 'name': '通用航空ETF基金'},
            {'ts_code': '159862.SZ', 'name': '食品ETF'},
            {'ts_code': '159231.SZ', 'name': '通用航空ETF华宝'},
            {'ts_code': '159268.SZ', 'name': '港股通消费50ETF'},
            {'ts_code': '159245.SZ', 'name': '港股通消费ETF'},
            {'ts_code': '159210.SZ', 'name': '港股汽车ETF'},
            {'ts_code': '159887.SZ', 'name': '银行ETF'},
            {'ts_code': '159392.SZ', 'name': '航空ETF'},
            {'ts_code': '159699.SZ', 'name': '恒生消费ETF'},
            {'ts_code': '159241.SZ', 'name': '航空航天ETF天弘'},
            {'ts_code': '159227.SZ', 'name': '航空航天ETF'},
            {'ts_code': '159208.SZ', 'name': '航天航空ETF'},
            {'ts_code': '159570.SZ', 'name': '港股通创新药ETF'},
            {'ts_code': '159316.SZ', 'name': '恒生创新药ETF'},
            {'ts_code': '159217.SZ', 'name': '港股通创新药ETF工银'},
            {'ts_code': '159567.SZ', 'name': '港股创新药ETF'},
            {'ts_code': '159981.SZ', 'name': '能源化工ETF'},
            {'ts_code': '159851.SZ', 'name': '金融科技ETF'},
            {'ts_code': '159529.SZ', 'name': '标普消费ETF'},
            {'ts_code': '159876.SZ', 'name': '有色龙头ETF'},
            {'ts_code': '159977.SZ', 'name': '创业板ETF天弘'},
            
            # 补充一些重要的上海交易所ETF
            {'ts_code': '510300.SH', 'name': '沪深300ETF'},
            {'ts_code': '510050.SH', 'name': '上证50ETF'},
            {'ts_code': '510500.SH', 'name': '中证500ETF'},
            {'ts_code': '512880.SH', 'name': '证券ETF'},
            {'ts_code': '518880.SH', 'name': '黄金ETF'},
            {'ts_code': '513100.SH', 'name': '纳斯达克ETF'},
            {'ts_code': '513500.SH', 'name': '标普500ETF'},
            {'ts_code': '513050.SH', 'name': '中概互联网ETF'},
            {'ts_code': '512000.SH', 'name': '券商ETF'},
            {'ts_code': '588000.SH', 'name': '科创50ETF'},
            {'ts_code': '512010.SH', 'name': '医药ETF'},
            {'ts_code': '512480.SH', 'name': '半导体ETF'},
            {'ts_code': '512760.SH', 'name': '芯片ETF'},
            {'ts_code': '512800.SH', 'name': '银行ETF'},
            {'ts_code': '512660.SH', 'name': '军工ETF'},
            {'ts_code': '512400.SH', 'name': '有色金属ETF'},
            {'ts_code': '512690.SH', 'name': '酒ETF'},
            {'ts_code': '515030.SH', 'name': '新能源汽车ETF'},
            {'ts_code': '513660.SH', 'name': '恒生ETF'},
            {'ts_code': '510900.SH', 'name': 'H股ETF'},
            {'ts_code': '513130.SH', 'name': '恒生科技ETF'},
            {'ts_code': '511260.SH', 'name': '国债ETF'},
            {'ts_code': '511380.SH', 'name': '可转债ETF'}
        ]
        full_etf_list = complete_etfs
        
        print(f"📊 ETF总数: {len(full_etf_list)}")
        return pd.DataFrame(full_etf_list)
    
    def get_etf_daily_data(self, ts_code, days=250):
        """
        使用yfinance获取ETF日线数据
        """
        try:
            # 添加随机延迟，避免请求过快
            time.sleep(random.uniform(0.3, 0.8))
            
            # 转换代码格式
            code_clean = ts_code.split('.')[0]
            if ts_code.endswith('.SH'):
                yf_code = f"{code_clean}.SS"
            else:
                yf_code = f"{code_clean}.SZ"
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 使用yfinance获取数据
            stock = yf.Ticker(yf_code)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty or len(df) < self.min_required_days:
                return None
            
            # 重置索引并规范列名
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'trade_date', 
                'Open': 'open', 
                'High': 'high', 
                'Low': 'low', 
                'Close': 'close', 
                'Volume': 'volume'
            })
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df
        except Exception as e:
            print(f"  ❌ 数据获取失败 {ts_code}: {e}")
            return None
    
    # ==================== 技术指标计算函数 ====================
    
    def calculate_momentum(self, prices):
        """计算动量因子"""
        periods = [20, 60, 120]  # 约1个月、3个月、6个月
        moms = []
        
        for p in periods:
            if len(prices) >= p:
                mom = prices.iloc[-1] / prices.iloc[-p] - 1
            else:
                mom = np.nan
            moms.append(mom)
        
        return moms
    
    def calculate_slope(self, prices, period=60):
        """计算趋势斜率"""
        if len(prices) < period:
            return np.nan
        
        log_prices = np.log(prices.iloc[-period:].values)
        x = np.arange(len(log_prices))
        
        try:
            slope, _, _, _, _ = linregress(x, log_prices)
            return slope
        except:
            return np.nan
    
    def calculate_volatility(self, returns, period=60):
        """计算年化波动率"""
        if len(returns) < period:
            return np.nan
        return np.std(returns.iloc[-period:]) * np.sqrt(252)
    
    def calculate_sharpe(self, returns, period=60):
        """计算年化夏普比率"""
        if len(returns) < period:
            return np.nan
        
        period_returns = returns.iloc[-period:]
        mean_return = np.mean(period_returns)
        std_return = np.std(period_returns)
        
        if std_return == 0:
            return np.nan
        
        return (mean_return / std_return) * np.sqrt(252)
    
    def calculate_adx(self, high, low, close, period=14):
        """
        计算平均趋向指数ADX - 使用ta库版本
        """
        if len(close) < period + 10:
            return np.nan
        
        try:
            # 使用ta库计算ADX
            adx_indicator = ta.trend.ADXIndicator(
                high=high, 
                low=low, 
                close=close, 
                window=period
            )
            adx = adx_indicator.adx()
            return adx.iloc[-1] if not adx.empty and not pd.isna(adx.iloc[-1]) else np.nan
        except Exception as e:
            return np.nan
    
    def calculate_ma200_filter(self, close):
        """计算200日均线过滤器"""
        if len(close) < 200:
            return np.nan
        
        ma200 = np.mean(close.iloc[-200:])
        current_price = close.iloc[-1]
        return 1 if current_price > ma200 else 0
    
    def calculate_atr(self, high, low, close, period=14):
        """
        计算平均真实波幅ATR - 使用ta库版本
        """
        if len(close) < period + 1:
            return np.nan
        
        try:
            # 使用ta库计算ATR
            atr_indicator = ta.volatility.AverageTrueRange(
                high=high, 
                low=low, 
                close=close, 
                window=period
            )
            atr = atr_indicator.average_true_range()
            return atr.iloc[-1] if not atr.empty and not pd.isna(atr.iloc[-1]) else np.nan
        except Exception as e:
            return np.nan
    
    def cross_sectional_zscores(self, factor_values):
        """截面标准化"""
        valid_values = [v for v in factor_values if not np.isnan(v)]
        
        if len(valid_values) < 2:
            return factor_values
        
        # 去极值
        try:
            winsorized = winsorize(valid_values, limits=[0.05, 0.05])
        except:
            winsorized = valid_values
        
        # 标准化
        mean = np.mean(winsorized)
        std = np.std(winsorized)
        
        if std == 0:
            return [0] * len(factor_values)
        
        # 将原始因子值替换为标准化后的值
        z_scores = []
        valid_index = 0
        for v in factor_values:
            if np.isnan(v):
                z_scores.append(np.nan)
            else:
                z_scores.append((winsorized[valid_index] - mean) / std)
                valid_index += 1
        
        return z_scores
    
    def generate_complete_rating(self):
        """
        生成完整的ETF评级和排名
        """
        print("🎯 开始生成完整ETF评级排名...")
        start_time = time.time()
        
        # 获取全市场ETF列表
        etf_list = self.get_all_etf_list()
        
        # 存储ETF详细数据
        etf_details = []
        successful_count = 0
        total_count = len(etf_list)
        
        print(f"📊 开始分析 {total_count} 只ETF...")
        
        # 对每个ETF计算因子
        for idx, row in etf_list.iterrows():
            ts_code = row['ts_code']
            name = row['name']
            
            # 每20个ETF显示一次进度
            if idx % 20 == 0:
                elapsed_time = time.time() - start_time
                etf_per_second = idx / elapsed_time if elapsed_time > 0 else 0
                remaining_etfs = total_count - idx
                estimated_remaining = remaining_etfs / etf_per_second if etf_per_second > 0 else 0
                
                print(f"⏳ 进度: {idx}/{total_count} ({idx/total_count*100:.1f}%) - "
                      f"成功: {successful_count} - "
                      f"预计剩余: {estimated_remaining/60:.1f}分钟")
            
            # 获取历史数据
            daily_data = self.get_etf_daily_data(ts_code, self.max_days)
            if daily_data is None or len(daily_data) < self.min_required_days:
                continue
            
            # 准备数据
            close_prices = daily_data['close']
            current_price = close_prices.iloc[-1]
            prev_close = close_prices.iloc[-2] if len(close_prices) >= 2 else current_price
            
            # 计算收益率
            returns = close_prices.pct_change().dropna()
            if len(returns) < self.min_required_days:
                continue
            
            # 计算各因子
            # 1. 动量因子
            mom_1m, mom_3m, mom_6m = self.calculate_momentum(close_prices)
            
            if np.isnan(mom_1m) or np.isnan(mom_3m) or np.isnan(mom_6m):
                momentum_combo = np.nan
            else:
                momentum_combo = (self.weight_mom_1m * mom_1m +
                                 self.weight_mom_3m * mom_3m +
                                 self.weight_mom_6m * mom_6m)
            
            # 计算趋势斜率
            slope = self.calculate_slope(close_prices)
            
            # 计算动量得分
            if np.isnan(momentum_combo) or np.isnan(slope):
                momentum_score = np.nan
            else:
                momentum_score = 0.7 * momentum_combo + 0.3 * slope
            
            # 2. 波动率因子
            volatility = self.calculate_volatility(returns)
            
            # 3. 夏普比率
            sharpe = self.calculate_sharpe(returns)
            
            # 4. 趋势质量因子
            adx = self.calculate_adx(daily_data['high'], daily_data['low'], daily_data['close'])
            ma200_filter = self.calculate_ma200_filter(daily_data['close'])
            
            if np.isnan(adx) or np.isnan(ma200_filter):
                trend_quality_score = np.nan
            else:
                trend_quality_score = self.weight_adx * adx + self.weight_ma200 * ma200_filter
            
            # 计算ATR用于挂单建议
            atr = self.calculate_atr(daily_data['high'], daily_data['low'], daily_data['close'])
            
            # 存储ETF数据
            etf_details.append({
                'ts_code': ts_code,
                'name': name,
                'current_price': current_price,
                'prev_close': prev_close,
                'price_change_pct': (current_price - prev_close) / prev_close if prev_close > 0 else 0,
                'momentum_score': momentum_score if not np.isnan(momentum_score) else 0,
                'volatility': volatility if not np.isnan(volatility) else 0,
                'sharpe': sharpe if not np.isnan(sharpe) else 0,
                'trend_quality': trend_quality_score if not np.isnan(trend_quality_score) else 0,
                'atr': atr if not np.isnan(atr) else 0,
                'mom_1m': mom_1m if not np.isnan(mom_1m) else 0,
                'mom_3m': mom_3m if not np.isnan(mom_3m) else 0,
                'mom_6m': mom_6m if not np.isnan(mom_6m) else 0
            })
            
            successful_count += 1
        
        total_time = time.time() - start_time
        print(f"✅ 数据处理完成! 有效ETF数量: {successful_count}/{total_count}")
        print(f"⏱️ 总耗时: {total_time/60:.2f}分钟")
        
        if not etf_details:
            print("❌ 没有足够的有效ETF数据")
            return
        
        # 因子标准化
        momentum_scores = [etf['momentum_score'] for etf in etf_details]
        volatility_scores = [-etf['volatility'] for etf in etf_details]  # 波动率取负值
        sharpe_scores = [etf['sharpe'] for etf in etf_details]
        trend_quality_scores = [etf['trend_quality'] for etf in etf_details]
        
        z_momentum = self.cross_sectional_zscores(momentum_scores)
        z_volatility = self.cross_sectional_zscores(volatility_scores)
        z_sharpe = self.cross_sectional_zscores(sharpe_scores)
        z_trend_quality = self.cross_sectional_zscores(trend_quality_scores)
        
        # 计算综合得分
        for i, etf in enumerate(etf_details):
            total_score = (self.weight_momentum * z_momentum[i] +
                          self.weight_volatility * z_volatility[i] +
                          self.weight_risk_adjusted * z_sharpe[i] +
                          self.weight_trend_quality * z_trend_quality[i])
            etf_details[i]['total_score'] = total_score
        
        # 按得分排序
        etf_details.sort(key=lambda x: x['total_score'], reverse=True)
        
        # 输出完整排名
        self.print_complete_ranking(etf_details)
        
        # 生成调仓建议
        self.generate_rebalancing_suggestions(etf_details)
        
        return etf_details
    
    def print_complete_ranking(self, etf_details):
        """打印完整排名报告"""
        print("\n" + "="*120)
        print("🎯 ETF完整综合评级排名")
        print("="*120)
        print(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 有效ETF总数: {len(etf_details)}")
        
        print(f"\n🏆 ETF综合排名 (前{self.top_n}):")
        print("-" * 120)
        print(f"{'排名':<4} {'代码':<12} {'名称':<20} {'当前价':<8} {'涨跌幅':<8} {'综合得分':<10} {'动量':<8} {'波动率':<8} {'夏普':<8} {'趋势质量':<10}")
        print("-" * 120)
        
        for i, etf in enumerate(etf_details[:self.top_n]):
            print(f"{i+1:<4} {etf['ts_code']:<12} {etf['name']:<20} {etf['current_price']:<8.3f} "
                  f"{etf['price_change_pct']:<8.2%} {etf['total_score']:<10.3f} "
                  f"{etf['momentum_score']:<8.3f} {etf['volatility']:<8.3f} "
                  f"{etf['sharpe']:<8.3f} {etf['trend_quality']:<10.3f}")
        
        # 显示排名分布统计
        print(f"\n📈 排名分布统计:")
        scores = [etf['total_score'] for etf in etf_details]
        print(f"   最高分: {max(scores):.3f}")
        print(f"   最低分: {min(scores):.3f}")
        print(f"   平均分: {np.mean(scores):.3f}")
        print(f"   中位数: {np.median(scores):.3f}")
        
        # 按类别显示前几名
        self.print_category_ranking(etf_details)
    
    def print_category_ranking(self, etf_details):
        """按类别显示排名"""
        # 简单的类别分类（根据名称关键词）
        categories = {
            '宽基指数': ['300', '50', '500', '1000', '创业板', '科创'],
            '行业主题': ['医药', '医疗', '半导体', '芯片', '新能源', '电池', '消费', '酒', '券商', '证券', '银行', '军工', '有色金属', '黄金'],
            '跨境QDII': ['纳指', '标普', '恒生', '港股', '中概', '德国', '日经'],
            '商品债券': ['国债', '黄金', '豆粕', '可转债']
        }
        
        print(f"\n🏷️  按类别排名 (各类别前5名):")
        print("-" * 80)
        
        for category, keywords in categories.items():
            category_etfs = []
            for etf in etf_details:
                if any(keyword in etf['name'] for keyword in keywords):
                    category_etfs.append(etf)
            
            if category_etfs:
                category_etfs.sort(key=lambda x: x['total_score'], reverse=True)
                print(f"\n📊 {category} ({len(category_etfs)}只):")
                for i, etf in enumerate(category_etfs[:5]):
                    print(f"   {i+1}. {etf['name']} - 得分: {etf['total_score']:.3f} (排名: {etf_details.index(etf)+1})")
    
    def generate_rebalancing_suggestions(self, etf_details):
        """生成调仓建议"""
        print(f"\n💡 推荐持仓 (前{self.recommend_n}名):")
        recommended_etfs = etf_details[:self.recommend_n]
        
        for i, etf in enumerate(recommended_etfs):
            print(f"{i+1}. {etf['name']} ({etf['ts_code']}) - 得分: {etf['total_score']:.3f}")
        
        # 挂单价格建议
        print(f"\n💰 挂单价格建议 (基于ATR波动率):")
        print("-" * 80)
        
        for etf in recommended_etfs:
            current_price = etf['current_price']
            atr = etf['atr']
            
            if atr > 0:
                # 买入建议区间
                buy_low = current_price - atr * 0.8
                buy_high = current_price - atr * 0.3
                # 保守买入价
                buy_conservative = current_price - atr * 0.5
                
                print(f"📈 {etf['name']}:")
                print(f"   当前价: {current_price:.3f}")
                print(f"   建议买入区间: {buy_low:.3f} - {buy_high:.3f}")
                print(f"   保守买入价: {buy_conservative:.3f}")
                print(f"   建议仓位: {100/self.recommend_n:.1f}% (等权重)")
            else:
                print(f"📈 {etf['name']}:")
                print(f"   当前价: {current_price:.3f}")
                print(f"   建议参考价: {current_price * 0.99:.3f} - {current_price * 1.01:.3f}")
        
        # 调仓建议
        print(f"\n⚡ 调仓操作建议:")
        print("1. 优先配置排名前3的ETF")
        print("2. 采用等权重分配资金")
        print("3. 使用建议价格区间进行限价挂单")
        print("4. 如已持仓但不在推荐列表，考虑逢高减仓")
        print("5. 建议单只ETF仓位不超过总资金的35%")
        print("="*120)
    
    def save_results_to_folders(self, etf_details):
        """将结果保存到不同的文件夹"""
        if not etf_details:
            print("❌ 没有数据可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # 保存完整排名到 complete_ratings 文件夹
        df_results = pd.DataFrame(etf_details)
        complete_filename = os.path.join(self.complete_ratings_folder, f'etf_complete_rating_{timestamp}.csv')
        df_results.to_csv(complete_filename, index=False, encoding='utf-8-sig')
        print(f"💾 完整排名已保存至: {complete_filename}")
        
        # 保存前100名到 top100_ratings 文件夹
        df_top100 = pd.DataFrame(etf_details[:100])
        top100_filename = os.path.join(self.top100_ratings_folder, f'etf_top100_rating_{timestamp}.csv')
        df_top100.to_csv(top100_filename, index=False, encoding='utf-8-sig')
        print(f"💾 前100名已保存至: {top100_filename}")
        
        # 显示文件夹信息
        print(f"\n📁 文件分类保存完成:")
        print(f"   📂 {self.complete_ratings_folder}/ - 完整排名文件")
        print(f"   📂 {self.top100_ratings_folder}/ - 前100名文件")

# 使用示例
def main():
    print("🚀 启动完整版ETF每日评级系统...")
    
    # 创建评级系统
    rating_system = CompleteETFDailyRating()
    
    try:
        # 生成完整评级
        start_time = time.time()
        results = rating_system.generate_complete_rating()
        end_time = time.time()
        
        total_time = end_time - start_time
        print(f"\n⏱️ 总执行时间: {total_time/60:.2f}分钟")
        
        if results:
            # 保存结果到分类文件夹
            rating_system.save_results_to_folders(results)
            
    except Exception as e:
        print(f"❌ 系统执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()