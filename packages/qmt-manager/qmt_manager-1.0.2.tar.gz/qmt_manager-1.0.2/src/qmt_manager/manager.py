#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QMT_Manager - QMT_XTQUANT交易接口封装库
版本: 1.0.0 | 创建日期: 2025-06-25
版权声明: 本代码受版权保护，未经授权禁止修改、隐藏或分发。
"""

import os
import sys
import time
import random
import datetime
import pandas as pd
import logging as log
from tabulate import tabulate
from datetime import datetime

# 添加打包的xtquant库到系统路径
def add_xtquant_path():
    try:
        lib_path = os.path.join(os.path.dirname(__file__), 'libs')
        if os.path.exists(lib_path) and lib_path not in sys.path:
            sys.path.insert(0, lib_path)
            print(f"已添加库路径: {lib_path}")
    except Exception as e:
        print(f"添加库路径时出错: {str(e)}")

add_xtquant_path()

try:
    from xtquant import xttrader, xtdata, xtconstant
    from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
    from xtquant.xttype import StockAccount
except ImportError:
    print("警告: 无法导入xtquant模块。请确保已正确配置国金QMT环境。")
    print("建议: 检查QMT路径是否正确，并重启QMT终端后重试。")
    raise

# 打印作者声明函数 - 不可修改的核心部分
def print_author_declaration():
    """打印不可修改的作者和版权声明"""
    print("\n" + "=" * 80)
    print("QMT_Manager - QMT_XTQUANT交易接口封装库 v1.0.0")
    print("-" * 80)
    print("作者: [量化交易汤姆猫] | 微信: QUANT0808")
    print("欢迎联系我：BUG反馈、功能完善、量化交流")
    print("量化资料库: https://quant0808.netlify.app")
    print("-" * 80)
    print("风险提示: 仅供参考，不构成投资建议，使用风险需自行承担")
    print("=" * 80 + "\n")

# 在模块加载时打印声明
print_author_declaration()

# 配置日志
log.basicConfig(
    level='INFO',
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class xtcb(XtQuantTraderCallback):
    def on_order_error(self, order_id, error_code, error_msg):
        log.error(f"【下单失败】订单 ID: {order_id}, 错误码: {error_code}, 错误信息: {error_msg}")

# 定义管理类
class XtQuantTraderManager:
    def __init__(self, path: str, acc: str, order_file='orders.csv'):
        self.path = path
        self.acc = acc
        self.order_file = order_file
        self.xt_trader = self._connect()
        # 检查连接状态
        if self.xt_trader is None:
            log.error("无法连接到QMT交易终端或订阅账户失败，部分功能将不可用")
            log.info("建议检查以下项目:")
            log.info("1. miniQMT交易端是否已启动")
            log.info("2. 账号是否正确")
            log.info("3. miniqmt路径是否正确")
        else:
            log.info("交易终端连接成功，可以正常使用")

        self.trade_rules = {
            '688': {'name': '科创板', 'min': 200, 'step': 1, 'slippage': 0.01, 'unit': '股'},
            '300': {'name': '创业板', 'min': 100, 'step': 100, 'slippage': 0.01, 'unit': '股'},
            '60': {'name': '沪市主板', 'min': 100, 'step': 100, 'slippage': 0.01, 'unit': '股'},
            '00': {'name': '深市主板', 'min': 100, 'step': 100, 'slippage': 0.01, 'unit': '股'},
            '50': {'name': '沪市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '51': {'name': '沪市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '52': {'name': '沪市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '53': {'name': '沪市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '56': {'name': '沪市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '58': {'name': '沪市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '15': {'name': '深市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '16': {'name': '深市ETF', 'min': 100, 'step': 100, 'slippage': 0.001, 'unit': '份'},
            '11': {'name': '可转债', 'min': 10, 'step': 10, 'slippage': 0.001, 'unit': '张'},
            '12': {'name': '可转债', 'min': 10, 'step': 10, 'slippage': 0.001, 'unit': '张'},
            '4': {'name': '北京股票', 'min': 0, 'step': 100, 'slippage': 0.01, 'unit': '股'},
            '8': {'name': '北京股票', 'min': 0, 'step': 100, 'slippage': 0.01, 'unit': '股'},
            '9': {'name': '北京股票', 'min': 0, 'step': 100, 'slippage': 0.01, 'unit': '股'},
        }
        self._init_order_table()

    def _connect(self) -> XtQuantTrader:
        """安全连接QMT交易终端 - 错误容错版"""
        try:
            session_id = random.randint(10000000, 99999999)
            xt_trader = XtQuantTrader(self.path, session_id)
            
            # 注册回调
            callback = xtcb()
            xt_trader.register_callback(callback)
            
            # 启动交易系统
            xt_trader.start()
            
            # 建立连接
            connect_id = xt_trader.connect()
            if connect_id != 0:
                error_msg = f"miniqmt链接失败，错误码: {connect_id}"
                log.error(error_msg)
                # 改为记录错误但不抛出异常
                return None  # 返回None表示连接失败
            
            log.info('miniqmt连接成功')
            
            # 订阅账户
            acc_id = StockAccount(self.acc)
            sub_res = xt_trader.subscribe(acc_id)
            if sub_res != 0:
                error_msg = f"账户订阅失败，错误码: {sub_res}"
                log.error(error_msg)
                # 返回None表示订阅失败
                return None
            
            log.info('账户订阅成功')
            return xt_trader
            
        except Exception as e:
            log.error(f"连接QMT时发生未预期的错误: {str(e)}")
            return None  # 在异常情况下也返回None

    def _init_order_table(self):
        columns = ['order_id', 'symbol', 'direction', 'volume', 'filled_volume', 'price', 'order_time', 
                   'status', 'retry_count', 'strategy_name', 'order_remark']
        if not pd.io.common.file_exists(self.order_file):
            pd.DataFrame(columns=columns).to_csv(self.order_file, index=False)

    def _append_order_to_csv(self, order_dict):
        df = pd.read_csv(self.order_file)
        df = pd.concat([df, pd.DataFrame([order_dict])], ignore_index=True)
        df.to_csv(self.order_file, index=False)

    def _update_order_in_csv(self, order_id, updates):
        df = pd.read_csv(self.order_file)
        mask = df['order_id'] == order_id
        for key, value in updates.items():
            df.loc[mask, key] = value
        df.to_csv(self.order_file, index=False)

    def query_stock_asset(self):
        asset = self.xt_trader.query_stock_asset(StockAccount(self.acc))
        asset_list = []
        asset_dict = {
            '账户类型': asset.account_type,
            '资金账户': asset.account_id,
            '可用资金': asset.cash,
            '冻结金额': asset.frozen_cash,
            '持仓市值': asset.market_value,
            '总资产': asset.total_asset
        }
        asset_list.append(asset_dict)
        asset_df = pd.DataFrame(asset_list)
        asset_df.set_index('资金账户', inplace=True)
        print(tabulate(asset_df,headers='keys', tablefmt='fancy_grid', showindex=False))
        return asset_df

    def _get_available_fund(self):
        asset = self.xt_trader.query_stock_asset(StockAccount(self.acc))
        return asset.cash if asset else 0

    def _get_available_pos(self, symbol):
        pos = self.xt_trader.query_stock_position(StockAccount(self.acc), symbol)
        return pos.can_use_volume if pos else 0

    def query_stock_orders(self):
        orders = self.xt_trader.query_stock_orders(StockAccount(self.acc))
        if not orders:
            print("当前没有委托订单。")
            return None
        order_list = []
        for order in orders:
            order_dict = {
                '资金账号': order.account_id,
                '证券代码': order.stock_code,
                '订单编号': order.order_id,
                '柜台合同编号': order.order_sysid,
                '报单时间': order.order_time,
                '委托类型': order.order_type,
                '委托数量': order.order_volume,
                '报价类型': order.price_type,
                '委托价格': order.price,
                '成交数量': order.traded_volume,
                '成交均价': order.traded_price,
                '委托状态': order.order_status,
                '委托状态描述': order.status_msg,
                '策略名称': order.strategy_name,
                '委托备注': order.order_remark,
            }
            order_list.append(order_dict)
        orders_df = pd.DataFrame(order_list)
        print(tabulate(orders_df, headers='keys', tablefmt='fancy_grid', showindex=False))
        return orders_df

    def query_stock_trades(self):
        trades = self.xt_trader.query_stock_trades(StockAccount(self.acc))
        if not trades:
            print("当前没有成交记录。")
            return None
        trade_list = []
        for trade in trades:
            trade_dict = {
                '资金账号': trade.account_id,
                '证券代码': trade.stock_code,
                '成交时间': trade.traded_time,
                '成交数量': trade.traded_volume,
                '成交金额': trade.traded_amount,
                '成交均价': trade.traded_price,
                '委托类型': trade.order_type,
                '交易编号': trade.traded_id,
            }
            trade_list.append(trade_dict)
        trades_df = pd.DataFrame(trade_list)
        trades_df['成交时间'] = pd.to_datetime(trades_df['成交时间'], unit='s', utc=True)
        trades_df['成交时间'] = trades_df['成交时间'].dt.tz_convert('Asia/Shanghai')
        trades_df['成交时间'] = trades_df['成交时间'].dt.strftime("%Y-%m-%d %H:%M:%S")
        trades_df['成交时间'] = pd.to_datetime(trades_df['成交时间'])
        trades_df.set_index('资金账号', inplace=True)
        print(tabulate(trades_df, headers='keys', tablefmt='fancy_grid', showindex=False))
        return trades_df

    def query_stock_positions(self):
        positions = self.xt_trader.query_stock_positions(StockAccount(self.acc))
        if not positions:
            print("当前没有持仓信息。")
            return None
        position_list = []
        for position in positions:
            position_dict = {
                '资金账号': position.account_id,
                '证券代码': position.stock_code,
                '持仓数量': position.volume,
                '可用数量': position.can_use_volume,
                '开仓价': position.open_price,
                '市值': position.market_value,
                '冻结数量': position.frozen_volume,
                '在途股份': position.on_road_volume,
                '昨夜拥股': position.yesterday_volume,
                '成本价': position.open_price
            }
            position_list.append(position_dict)
        pos_df = pd.DataFrame(position_list)
        log.info('======持仓信息======')
        log.info((tabulate(pos_df, headers='keys', tablefmt='fancy_grid', showindex=False)))
        return pos_df

    def get_board(self, symbol):
        prefix = symbol[:3] if symbol.startswith('688') else symbol[:2]
        rule = self.trade_rules.get(prefix)
        if rule:
            name = rule['name']
            if name in ['沪市主板', '深市主板']:
                return '主板'
            elif name == '创业板':
                return '创业板'
            elif name == '科创板':
                return '科创板'
            elif name == '北京股票':
                return '北交所'
            else:
                return '其他'
        return '其他'

    def _check_price_cage(self, symbol, order_side, order_price=None):
        board = self.get_board(symbol)
        if board == '其他':
            print(f"【价格笼子】{symbol} 不属于价格笼子生效范围，跳过检查。")
            return True
        now_time = datetime.datetime.now().time()
        start_time = datetime.time(9, 25)
        end_time = datetime.time(14, 57)
        if not (start_time <= now_time <= end_time):
            print(f"【价格笼子】当前时间 {now_time.strftime('%H:%M:%S')} 不在生效时间 (09:25-14:57) 内，跳过检查。")
            return True
        reference_price = self._get_last_price(symbol)
        if reference_price is None or reference_price <= 0:
            print(f"【价格笼子】{symbol} 参考价无效 ({reference_price})，跳过检查。")
            return True
        if board in ['主板', '创业板']:
            if order_side == 'buy':
                upper_limit = max(reference_price * 1.02, reference_price + 0.1)
                if order_price > upper_limit:
                    print(f"【价格笼子校验失败】{symbol} 买入委托价 {order_price:.2f} 过高。")
                    return False
            elif order_side == 'sell':
                lower_limit = min(reference_price * 0.98, reference_price - 0.1)
                if order_price < lower_limit:
                    print(f"【价格笼子校验失败】{symbol} 卖出委托价 {order_price:.2f} 过低。")
                    return False
        elif board == '北交所':
            if order_side == 'buy':
                upper_limit = max(reference_price * 1.05, reference_price + 0.1)
                if order_price > upper_limit:
                    print(f"【价格笼子校验失败】{symbol} 买入委托价 {order_price:.2f} 过高。")
                    return False
            elif order_side == 'sell':
                lower_limit = min(reference_price * 0.95, reference_price - 0.1)
                if order_price < lower_limit:
                    print(f"【价格笼子校验失败】{symbol} 卖出委托价 {order_price:.2f} 过低。")
                    return False
        elif board == '科创板':
            if order_side == 'buy':
                upper_limit = round(reference_price * 1.02, 2)
                if order_price > upper_limit:
                    print(f"【价格笼子校验失败】{symbol} 买入委托价 {order_price:.2f} 过高。")
                    return False
            elif order_side == 'sell':
                lower_limit = round(reference_price * 0.98, 2)
                if order_price < lower_limit:
                    print(f"【价格笼子校验失败】{symbol} 卖出委托价 {order_price:.2f} 过低。")
                    return False
        print(f"【价格笼子校验通过】{symbol} 委托价 {order_price:.2f} 在允许范围内。")
        return True

    def _calculate_commission(self, symbol, price, volume):
        amount = price * volume
        commission = amount * 0.0002
        return max(commission, 5)

    def _get_last_price(self, symbol):
        try:
            data = xtdata.get_full_tick([symbol])
            last_price = data[symbol]['lastPrice']
            print(last_price)
            return last_price
        except Exception as e:
            print(f"【行情获取失败】{symbol} 错误:{str(e)}")
            return None

    def _get_security_rule(self, symbol):
        code = symbol.split('.')[0] if '.' in symbol else symbol
        for prefix in self.trade_rules:
            if code.startswith(prefix):
                return self.trade_rules[prefix]
        return {'name': '默认', 'min': 100, 'step': 100, 'slippage': 0.01, 'unit': '股'}

    def _adjust_volume(self, symbol, volume):
        rule = self._get_security_rule(symbol)
        if rule['min'] == 0:
            print(f"【交易禁止】{symbol} 北交所品种不支持交易")
            return 0
        adjusted = max(rule['min'], volume) // rule['step'] * rule['step']
        if adjusted != volume:
            print(f"【数量调整】{symbol} {volume}{rule['unit']} -> {adjusted}{rule['unit']}")
        return int(adjusted)

    def buy(self, symbol, volume, price=None, strategy_name='', order_remark='', retry_count=0):
        try:
            adj_volume = self._adjust_volume(symbol, volume)
            if adj_volume <= 0:
                return -1
            if not symbol or adj_volume <= 0:
                print("【参数错误】证券代码或数量无效")
                return -1
            rule = self._get_security_rule(symbol)
            last_price = self._get_last_price(symbol)
            if last_price is None or last_price <= 0:
                print(f"【行情无效】{symbol} 获取最新价失败")
                return -1
            order_price = price if price is not None else last_price
            required_fund = order_price * adj_volume
            commission = self._calculate_commission(symbol, order_price, adj_volume)
            available_fund = self._get_available_fund()
            if available_fund < required_fund + commission:
                print(f"【资金不足】可用资金:{available_fund:.2f}元，所需资金:{required_fund+commission:.2f}元(含手续费{commission:.2f}元)")
                return -1
            
            final_price = round(last_price * (1 + rule['slippage']), 3) if price is None else round(float(price), 3)
            price_type = xtconstant.LATEST_PRICE if price is None else xtconstant.FIX_PRICE
            strategy_name = str(strategy_name) if pd.notna(strategy_name) else ''
            order_remark = str(order_remark) if pd.notna(order_remark) else ''
            
            # 尝试下单
            order_id = self.xt_trader.order_stock(
                StockAccount(self.acc), symbol, xtconstant.STOCK_BUY, adj_volume,
                price_type, final_price, strategy_name, order_remark
            )
            
            if order_id > 0:
                order_time = time.time()
                order_info = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'direction': 'buy',
                    'volume': adj_volume,
                    'filled_volume': 0,
                    'price': final_price if price is None else price,
                    'order_time': order_time,
                    'status': 'submitted',
                    'retry_count': retry_count,
                    'strategy_name': strategy_name,
                    'order_remark': order_remark
                }
                self._append_order_to_csv(order_info)
                print(f"【买入委托成功】{symbol} 价格:{'市价' if price is None else price} 数量:{adj_volume}{rule['unit']} 委托编号:{order_id}")
                return order_id
            else:
                print(f"【买入委托失败】{symbol} 错误码:{order_id}")
                return order_id
        except ConnectionError as e:
            print(f"【网络错误】下单时发生网络连接问题: {str(e)}")
            return -1
        except ValueError as e:
            print(f"【参数错误】下单时发生参数错误: {str(e)}")
            return -1
        except AttributeError as e:
            print(f"【API错误】下单时发生属性错误，可能由于 QMT 返回数据异常: {str(e)}")
            return -1
        except Exception as e:
            print(f"【下单异常】买入 {symbol} 时发生未知错误: {str(e)}")
            return -1


    def sell(self, symbol, volume, price=None, strategy_name='', order_remark='', retry_count=0):
        try:
            adj_volume = self._adjust_volume(symbol, volume)
            if adj_volume <= 0:
                return -1
            if not symbol or adj_volume <= 0:
                print("【参数错误】证券代码或数量无效")
                return -1
            rule = self._get_security_rule(symbol)
            last_price = self._get_last_price(symbol)
            if last_price is None or last_price <= 0:
                print(f"【行情无效】{symbol} 获取最新价失败")
                return -1
            
            final_price = round(last_price * (1 - rule['slippage']), 3) if price is None else round(float(price), 3)
            price_type = xtconstant.LATEST_PRICE if price is None else xtconstant.FIX_PRICE
            strategy_name = str(strategy_name) if pd.notna(strategy_name) else ''
            order_remark = str(order_remark) if pd.notna(order_remark) else ''
            
            # 尝试下单
            order_id = self.xt_trader.order_stock(
                StockAccount(self.acc), symbol, xtconstant.STOCK_SELL, adj_volume,
                price_type, final_price, strategy_name, order_remark
            )
            
            if order_id > 0:
                order_time = time.time()
                order_info = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'direction': 'sell',
                    'volume': adj_volume,
                    'filled_volume': 0,
                    'price': final_price if price is None else price,
                    'order_time': order_time,
                    'status': 'submitted',
                    'retry_count': retry_count,
                    'strategy_name': strategy_name,
                    'order_remark': order_remark
                }
                self._append_order_to_csv(order_info)
                print(f"【卖出委托成功】{symbol} 价格:{'市价' if price is None else price} 数量:{adj_volume}{rule['unit']} 委托编号:{order_id}")
                return order_id
            else:
                print(f"【卖出委托失败】{symbol} 错误码:{order_id}")
                return order_id
        except ConnectionError as e:
            print(f"【网络错误】下单时发生网络连接问题: {str(e)}")
            return -1
        except ValueError as e:
            print(f"【参数错误】下单时发生参数错误: {str(e)}")
            return -1
        except AttributeError as e:
            print(f"【API错误】下单时发生属性错误，可能由于 QMT 返回数据异常: {str(e)}")
            return -1
        except Exception as e:
            print(f"【下单异常】卖出 {symbol} 时发生未知错误: {str(e)}")
            return -1

    def cancel_order(self, order_id):
        """撤消指定订单"""
        try:
            result = self.xt_trader.cancel_order_stock(StockAccount(self.acc), order_id)
            if result == 0:
                print(f"【撤单成功】订单 {order_id}")
                self._update_order_in_csv(order_id, {'status': 'canceled'})
            else:
                print(f"【撤单失败】订单 {order_id} 错误码: {result}")
        except Exception as e:
            print(f"【撤单异常】订单 {order_id} 错误: {str(e)}")

    def check_and_resubmit(self):
        """检查并补单未完全成交的订单"""
        try:
            df = pd.read_csv(self.order_file)
            current_time = time.time()
            for index, row in df.iterrows():
                # 只处理状态为 'submitted' 且超过 30 秒的订单
                if row['status'] == 'submitted' and current_time - row['order_time'] >= 30:
                    order_id = row['order_id']
                    print(f"【检查订单】订单 {order_id}")
                    
                    # 查询订单状态
                    res = self.xt_trader.query_stock_order(StockAccount(self.acc), order_id)
                    if res is None:
                        print(f"【查询失败】订单 {order_id} 不存在")
                        self._update_order_in_csv(order_id, {'status': 'failed'})
                        continue
                    
                    # 更新成交量
                    filled_volume = res.traded_volume
                    self._update_order_in_csv(order_id, {'filled_volume': filled_volume})
                    
                    # 如果订单已完全成交或取消，无需补单
                    if filled_volume == row['volume']:
                        print(f"【订单已成】{order_id}")
                        self._update_order_in_csv(order_id, {'status': 'filled'})
                        continue
                    if res.order_status == xtconstant.ORDER_CANCELED:
                        print(f"【订单已取消】{order_id}")
                        self._update_order_in_csv(order_id, {'status': 'canceled'})
                        continue
                    
                    # 未完全成交且重试次数小于 3，执行撤单和补单
                    if row['retry_count'] < 3:
                        self.cancel_order(order_id)  # 撤单
                        remaining_volume = row['volume'] - filled_volume
                        new_order_id = self.sell(row['symbol'], remaining_volume, row['price'])
                        if new_order_id > 0:
                            print(f"【补单成功】新订单 {new_order_id}")
                            self._update_order_in_csv(order_id, {'retry_count': row['retry_count'] + 1})
                        else:
                            print(f"【补单失败】订单 {order_id}")
                            self._update_order_in_csv(order_id, {'status': 'failed'})
                    else:
                        print(f"【补单终止】{order_id} 重试次数已达上限")
                        self._update_order_in_csv(order_id, {'status': 'failed'})
                # 不满足补单条件时保持沉默
        except Exception as e:
            print(f"【检查异常】发生错误: {str(e)}")



    def _pass_order(self, **kwargs):
        print("开始调用 order_stock")
        try:
            seq = self.xt_trader.order_stock(
                kwargs['account'], kwargs['stock_code'], kwargs['order_type'],
                kwargs['order_volume'], kwargs['price_type'], kwargs['price'],
                kwargs['strategy_name'], kwargs['order_remark']
            )
            print(f"order_stock 返回值: {seq}")
            return seq
        except Exception as e:
            print(f"异常类型: {type(e).__name__}, 错误信息: {str(e)}")
            return -1
    def is_trading_time(self,max_weekday=4, start_hour=9, end_hour=14, start_minute=0, include_pre_open='否'):
        """
        检测当前时间是否在交易时间内。

        参数:
            max_weekday (int): 交易日的最大星期值（0-6，0为星期一，4为星期五），默认为 4。
            start_hour (int): 交易开始的小时，默认为 9。
            end_hour (int): 交易结束的小时，默认为 14。
            start_minute (int): 交易开始的分钟，默认为 0。
            include_pre_open (str): 是否包含集合竞价时间，'是' 或 '否'，默认为 '否'。

        返回:
            bool: 如果当前时间在交易时间内，返回 True；否则返回 False。
        """
        # 设置集合竞价时间
        pre_open_minute = 15 if include_pre_open == '是' else 30

        # 获取当前时间
        now = datetime.now()
        weekday = now.weekday()  # 0-6，0 为星期一
        hour = now.hour
        minute = now.minute

        # 检查是否为交易日
        if weekday <= max_weekday:
            # 检查小时是否在交易范围内
            if start_hour <= hour <= end_hour:
                # 特殊处理 9 点的情况
                if hour == start_hour:
                    return minute >= pre_open_minute
                return minute >= start_minute
            print('非交易时间')
            return False
        else:
            print('周末')
            return False
        
    def is_trading_time(max_weekday=4, start_hour=9, end_hour=14, start_minute=0, include_pre_open='否'):
        """
        检测当前时间是否在交易时间内。

        参数:
            max_weekday (int): 交易日的最大星期值（0-6，0为星期一，4为星期五），默认为 4。
            start_hour (int): 交易开始的小时，默认为 9。
            end_hour (int): 交易结束的小时，默认为 14。
            start_minute (int): 交易开始的分钟，默认为 0。
            include_pre_open (str): 是否包含集合竞价时间，'是' 或 '否'，默认为 '否'。

        返回:
            bool: 如果当前时间在交易时间内，返回 True；否则返回 False。
        """
        # 设置集合竞价时间
        pre_open_minute = 15 if include_pre_open == '是' else 30

        # 获取当前时间
        now = datetime.now()
        weekday = now.weekday()  # 0-6，0 为星期一
        hour = now.hour
        minute = now.minute

        # 检查是否为交易日
        if weekday <= max_weekday:
            # 检查小时是否在交易范围内
            if start_hour <= hour <= end_hour:
                # 特殊处理 9 点的情况
                if hour == start_hour:
                    return minute >= pre_open_minute
                return minute >= start_minute
            print('非交易时间')
            return False
        else:
            print('周末')
            return False
    
    def  check_symbol_is_limit_down(self,symbol):
        try:
            data = xtdata.get_instrument_detail(symbol)
        except Exception as e:
            log.warning('获取标的基础信息失败：{e}')
            return None

        up_stop_price = data['UpStopPrice']
        down_stop_price = data['DownStopPrice']
        try:
            lastprice = xtdata.get_full_tick([symbol])
            lastprice = lastprice[symbol]['lastPrice']
        except Exception as e:
            log.warning('获取最新价失败：{e}')
            return None
        
        if lastprice >= up_stop_price:
            log.info(f'标的{symbol}涨停')
            return '涨停'
        elif lastprice <= down_stop_price:
            log.info(f'标的{symbol}跌停')
            return  '涨停'
        else:
            log.info(f'标的{symbol}未涨停、未跌停')
            return  '正常'

    def cancel_all_orders(self):
        cancel_orders = self.xt_trader.query_stock_orders(StockAccount(self.acc),True)
        if not cancel_orders:
            print("当前没有委托订单。")
            return False
        order_list = []
        for order in cancel_orders:
            order_dict = {
                '资金账号': order.account_id,
                '证券代码': order.stock_code,
                '订单编号': order.order_id,
                '柜台合同编号': order.order_sysid,
                '报单时间': order.order_time,
                '委托类型': order.order_type,
                '委托数量': order.order_volume,
                '报价类型': order.price_type,
                '委托价格': order.price,
                '成交数量': order.traded_volume,
                '成交均价': order.traded_price,
                '委托状态': order.order_status,
                '委托状态描述': order.status_msg,
                '策略名称': order.strategy_name,
                '委托备注': order.order_remark,
            }
            order_list.append(order_dict)
        orders_df = pd.DataFrame(order_list) #可以撤单的委托

        撤销成功数 = 0
        for _,row in orders_df['订单编号']:
            order_id = row['订单编号']
            stock_code = row['证券代码']
            try:
                cancel_res = self.xt_trader.cancel_order_stock(StockAccount(self.acc),order_id)
                if cancel_res == 0:
                    log.info(f"{stock_code} | {order_id} | 撤单成功")
                    撤销成功数 += 1
                else:
                    log.warning(f"{stock_code} | {order_id} | 撤单失败")
            except Exception as e:
                log.warning(f'撤单操作失败，{str(e)}')

        log.info(f"【全部撤单】已成功撤销 {撤销成功数}/{len(orders_df)} 个订单")
        return 撤销成功数>0


    def cancel_buy_orders(self):
        cancel_orders = self.xt_trader.query_stock_orders(StockAccount(self.acc),True)
        if not cancel_orders:
            log.info("当前没有委托订单。")
            return False
        
        order_list = []
        for order in cancel_orders:
            order_dict = {
                '资金账号': order.account_id,
                '证券代码': order.stock_code,
                '订单编号': order.order_id,
                '柜台合同编号': order.order_sysid,
                '报单时间': order.order_time,
                '委托类型': order.order_type,
                '委托数量': order.order_volume,
                '报价类型': order.price_type,
                '委托价格': order.price,
                '成交数量': order.traded_volume,
                '成交均价': order.traded_price,
                '委托状态': order.order_status,
                '委托状态描述': order.status_msg,
                '策略名称': order.strategy_name,
                '委托备注': order.order_remark,
            }
            order_list.append(order_dict)
        orders_df = pd.DataFrame(order_list) #可以撤单的委托

        撤销成功数 = 0
        buy_orders_df = orders_df[orders_df['委托类型'] == xtconstant.STOCK_BUY]

        for _,row in buy_orders_df['订单编号']:
            order_id = row['订单编号']
            stock_code = row['证券代码']
            try:
                cancel_res = self.xt_trader.cancel_order_stock(StockAccount(self.acc),order_id)
                if cancel_res == 0:
                    log.info(f"{stock_code} | {order_id} | 撤单成功")
                    撤销成功数 += 1
                else:
                    log.warning(f"{stock_code} | {order_id} | 撤单失败")
            except Exception as e:
                log.warning(f'撤单操作失败，{str(e)}')

        log.info(f"【买入撤单】已成功撤销 {撤销成功数}/{len(buy_orders_df)} 个订单")
        return 撤销成功数>0

    def cancel_sell_orders(self):
        cancel_orders = self.xt_trader.query_stock_orders(StockAccount(self.acc),True)
        if not cancel_orders:
            log.info("当前没有委托订单。")
            return False
        
        order_list = []
        for order in cancel_orders:
            order_dict = {
                '资金账号': order.account_id,
                '证券代码': order.stock_code,
                '订单编号': order.order_id,
                '柜台合同编号': order.order_sysid,
                '报单时间': order.order_time,
                '委托类型': order.order_type,
                '委托数量': order.order_volume,
                '报价类型': order.price_type,
                '委托价格': order.price,
                '成交数量': order.traded_volume,
                '成交均价': order.traded_price,
                '委托状态': order.order_status,
                '委托状态描述': order.status_msg,
                '策略名称': order.strategy_name,
                '委托备注': order.order_remark,
            }
            order_list.append(order_dict)
        orders_df = pd.DataFrame(order_list) #可以撤单的委托

        撤销成功数 = 0
        sell_orders_df = orders_df[orders_df['委托类型'] == xtconstant.STOCK_SELL]

        for _,row in sell_orders_df['订单编号']:
            order_id = row['订单编号']
            stock_code = row['证券代码']
            try:
                cancel_res = self.xt_trader.cancel_order_stock(StockAccount(self.acc),order_id)
                if cancel_res == 0:
                    log.info(f"{stock_code} | {order_id} | 撤单成功")
                    撤销成功数 += 1
                else:
                    log.warning(f"{stock_code} | {order_id} | 撤单失败")
            except Exception as e:
                log.warning(f'撤单操作失败，{str(e)}')

        log.info(f"【卖出撤单】已成功撤销 {撤销成功数}/{len(sell_orders_df)} 个订单")
        return 撤销成功数>0

    def cancel_symbol_orders(self,symbol):
        cancel_orders = self.xt_trader.query_stock_orders(StockAccount(self.acc),True)
        if not cancel_orders:
            log.info(f"{symbol}当前没有委托订单。")
            return False
        order_list = []
        for order in cancel_orders:
            order_dict = {
                '资金账号': order.account_id,
                '证券代码': order.stock_code,
                '订单编号': order.order_id,
                '柜台合同编号': order.order_sysid,
                '报单时间': order.order_time,
                '委托类型': order.order_type,
                '委托数量': order.order_volume,
                '报价类型': order.price_type,
                '委托价格': order.price,
                '成交数量': order.traded_volume,
                '成交均价': order.traded_price,
                '委托状态': order.order_status,
                '委托状态描述': order.status_msg,
                '策略名称': order.strategy_name,
                '委托备注': order.order_remark,
            }
            order_list.append(order_dict)
        orders_df = pd.DataFrame(order_list) #可以撤单的委托

        撤销成功数 = 0
        symbol_orders_df = orders_df[orders_df['证券代码'] == symbol]

        for _,row in symbol_orders_df['订单编号']:
            order_id = row['订单编号']
            stock_code = row['证券代码']
            try:
                cancel_res = self.xt_trader.cancel_order_stock(StockAccount(self.acc),order_id)
                if cancel_res == 0:
                    log.info(f"{stock_code} | {order_id} | 撤单成功")
                    撤销成功数 += 1
                else:
                    log.warning(f"{stock_code} | {order_id} | 撤单失败")
            except Exception as e:
                log.warning(f'撤单操作失败，{str(e)}')

        log.info(f"【卖出撤单】已成功撤销 {撤销成功数}/{len(symbol_orders_df)} 个订单")
        return 撤销成功数>0

    def all_sell(self):
        positions = self.xt_trader.query_stock_positions(StockAccount(self.acc))
        if not positions:
            print("当前没有持仓信息。")
            return None
        position_list = []
        for position in positions:
            position_dict = {
                '资金账号': position.account_id,
                '证券代码': position.stock_code,
                '持仓数量': position.volume,
                '可用数量': position.can_use_volume,
                '开仓价': position.open_price,
                '市值': position.market_value,
                '冻结数量': position.frozen_volume,
                '在途股份': position.on_road_volume,
                '昨夜拥股': position.yesterday_volume,
                '成本价': position.open_price
            }
            position_list.append(position_dict)
        pos_df = pd.DataFrame(position_list)

        res = pos_df.loc[pos_df['可用数量']>0,['证券代码','可用数量']]
        trade_list = list(res.to_records(index=False))
        log.info(f'持有股数{len(trade_list)}')
        for stock_code ,can_use_volume in trade_list:
            self.sell(stock_code,can_use_volume)
        return True
    
    # ================= 元数据保护 =================
    def __str__(self):
        return f"XtQuantTraderManager(账户: {self.acc}, 版本: 2.0.0)"
    
    def __repr__(self):
        return f"<XtQuantTraderManager at {hex(id(self))}>"
    
    # 防止用户修改声明打印行为
    def _disable_declaration_modification(self):
        raise AttributeError("禁止修改作者声明功能")

    # 重写属性设置方法
    print_author_declaration = property(None, lambda self, value: self._disable_declaration_modification())
       
        
if __name__ == "__main__":
    # 测试代码
    print("==== XtQuantTraderManager 自测模式 ====")
    manager = XtQuantTraderManager(
        path=r"D:\国金QMT交易端模拟\userdata_mini", 
        acc="123456"
    )
    print("自测完成。正常使用时请移除这段测试代码。")