#  Copyright (c)  billpwchan - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#   Proprietary and confidential
#   Written by Bill Chan <billpwchan@hotmail.com>, 2020

import datetime
import configparser
from futu import *


class FutuTrade():
    def __init__(self):
        config = configparser.ConfigParser()

        self.quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quote_ctx.close()  # 关闭当条连接，FutuOpenD会在1分钟后自动取消相应股票相应类型的订阅

    def __del__(self):
        self.quote_ctx.close() # 关闭当条连接，FutuOpenD会在1分钟后自动取消相应股票相应类型的订阅

    def get_market_state(self):
        return self.quote_ctx.get_global_state()

    def save_historical_data(self, stock_code, start_date, end_date, k_type):
        out_dir = f'./data/{stock_code}'
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        output_path = f'./data/{stock_code}/{stock_code}_{start_date}_1M.csv'
        # Ensure update current day's 1M data
        if os.path.exists(output_path) and start_date != str(datetime.today().date()):
            return False
        # Request Historical K-line Data (Daily)
        ret, data, page_req_key = self.quote_ctx.request_history_kline(stock_code, start=start_date,
                                                                       end=end_date,
                                                                       ktype=k_type, autype=AuType.QFQ,
                                                                       fields=[KL_FIELD.ALL],
                                                                       max_count=1000, page_req_key=None,
                                                                       extended_time=False)
        if ret == RET_OK:
            data.to_csv(output_path, index=False)
        else:
            print('Historical Data Store Error:', data)
        return True

    def update_1M_data(self, stock_code):
        for i in range(365 * 2):
            day = datetime.today() - timedelta(days=i)
            if not self.save_historical_data(stock_code, str(day.date()), str(day.date()),
                                             KLType.K_1M):
                continue
            time.sleep(0.55)


class StockQuoteHandler(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(StockQuoteHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("StockQuoteTest ", data)  # StockQuote自己的处理逻辑
        return RET_OK, data


def display_result(ret, data):
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)


def update_hsi_constituents(input_file):
    hsi_constituents = pd.read_excel(input_file, index_col=0, engine='openpyxl')
    hsi_constituents = hsi_constituents.iloc[1::2].index.tolist()  # even
    hsi_constituents = ['.'.join(item.split('.')[::-1]) for item in hsi_constituents]
    with open(f'./data/HSI.Constituents/HSI_constituents_{datetime.today().date()}.json', 'w+') as f:
        json.dump(hsi_constituents, f)


def get_hsi_constituents(input_file):
    with open(input_file, 'r') as f:
        return json.load(f)
