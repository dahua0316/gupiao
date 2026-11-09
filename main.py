import akshare as ak
import pandas as pd
import datetime


# 获取A股历史数据（支持个股和指数）
def get_a_stock_data(symbol, start_date):
    try:
        # 示例：上证指数代码 "sh000001"，个股如贵州茅台 "sh600519"
        if symbol.startswith("sh") or symbol.startswith("sz"):
            stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date)
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data.set_index('日期', inplace=True)
            stock_data.rename(columns={'收盘': 'Close', '最高': 'High', '最低': 'Low'}, inplace=True)
            return stock_data
        else:
            print("股票代码格式错误，应以'sh'或'sz'开头，例如：sh600519")
            return None
    except Exception as e:
        print(f"数据获取失败：{e}")
        return None


# 计算均线与历史极值
def calculate_indicators(data):
    # 计算均线（10日与50日）
    data['Short_MA'] = data['Close'].rolling(window=10, min_periods=1).mean()
    data['Long_MA'] = data['Close'].rolling(window=50, min_periods=1).mean()

    # 历史最高价与最低价
    historical_max = data['High'].max()
    historical_min = data['Low'].min()
    return data, historical_max, historical_min


# 判断买入信号
def check_buy_signal(data, current_price, historical_min):
    # 条件1：短期均线上穿长期均线
    ma_cross = (data['Short_MA'].iloc[-1] > data['Long_MA'].iloc[-1]) and \
               (data['Short_MA'].iloc[-2] <= data['Long_MA'].iloc[-2])

    # 条件2：当前价格低于历史均值（可调整阈值）
    price_ratio = (current_price - historical_min) / (historical_max - historical_min)
    price_condition = price_ratio < 0.5  # 价格处于历史区间下半部分

    return ma_cross and price_condition


# 主函数
def main():
    symbol = "sh600519"  # 示例：贵州茅台（sh600519），上证指数 sh000001
    start_date = "20000101"  # 尽可能早的日期

    # 获取数据
    data = get_a_stock_data(symbol, start_date)
    if data is None or data.empty:
        return

    # 计算指标
    data, historical_max, historical_min = calculate_indicators(data)
    current_price = data['Close'].iloc[-1]

    # 判断买入信号
    buy_signal = check_buy_signal(data, current_price, historical_min)

    # 输出结果
    print(f"\n标的：{symbol}")
    print(f"当前价格：{current_price:.2f}元")
    print(f"历史最高价：{historical_max:.2f}元")
    print(f"历史最低价：{historical_min:.2f}元")
    print("----")
    print("买入信号：", "符合条件，建议关注！" if buy_signal else "未触发策略，保持观望")


if __name__ == "__main__":
    main()