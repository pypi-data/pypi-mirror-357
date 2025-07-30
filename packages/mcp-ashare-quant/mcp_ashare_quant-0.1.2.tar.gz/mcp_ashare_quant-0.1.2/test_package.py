#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 mcp-ashare-quant 包的使用示例
"""

def test_import():
    """测试包导入"""
    print("=== 测试包导入 ===")
    try:
        # 方式1：直接从包导入
        from mcp_ashare_quant import get_price, MA, BOLL, MACD
        print("✓ 成功从包根目录导入主要函数")
        
        # 方式2：从子模块导入
        from mcp_ashare_quant.ashare import get_price as get_price2
        from mcp_ashare_quant.mytt import MA as MA2
        print("✓ 成功从子模块导入函数")
        
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_basic_usage():
    """测试基本使用"""
    print("\n=== 测试基本使用 ===")
    try:
        from mcp_ashare_quant import get_price, MA
        
        # 获取股票数据
        print("获取上证指数数据...")
        df = get_price('sh000001', frequency='1d', count=5)
        print(f"数据形状: {df.shape}")
        print("数据列:", df.columns.tolist())
        
        # 计算技术指标
        close_prices = df['close'].tolist()
        ma5 = MA(close_prices, 5)
        print(f"MA5 计算结果: {ma5}")
        
        return True
    except Exception as e:
        print(f"✗ 基本使用测试失败: {e}")
        return False

def test_package_info():
    """测试包信息"""
    print("\n=== 测试包信息 ===")
    try:
        import mcp_ashare_quant
        print(f"包版本: {mcp_ashare_quant.__version__}")
        print(f"包作者: {mcp_ashare_quant.__author__}")
        print(f"可用函数: {mcp_ashare_quant.__all__}")
        return True
    except Exception as e:
        print(f"✗ 包信息获取失败: {e}")
        return False

if __name__ == "__main__":
    print("MCP A股量化分析包测试")
    print("=" * 50)
    
    success = True
    success &= test_import()
    success &= test_basic_usage() 
    success &= test_package_info()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ 所有测试通过！")
        print("\n使用示例:")
        print("```python")
        print("from mcp_ashare_quant import get_price, MA, BOLL, MACD")
        print("df = get_price('sh000001', count=10)")
        print("ma5 = MA(df['close'].tolist(), 5)")
        print("```")
    else:
        print("✗ 部分测试失败，请检查包安装")
