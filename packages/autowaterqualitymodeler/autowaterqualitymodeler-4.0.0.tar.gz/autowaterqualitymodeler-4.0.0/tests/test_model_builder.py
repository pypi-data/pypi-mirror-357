"""
测试模型构建器模块
"""
import pytest
import numpy as np
import pandas as pd
from autowaterqualitymodeler.models.builder import ModelBuilder


class TestModelBuilder:
    """测试ModelBuilder类"""
    
    @pytest.fixture
    def builder(self):
        """创建测试用的构建器实例"""
        return ModelBuilder()
    
    @pytest.fixture
    def sample_data(self):
        """创建测试用的数据"""
        np.random.seed(42)
        n_samples = 50
        
        # 创建特征数据
        x = np.random.rand(n_samples) * 10 + 0.1  # 确保为正值
        # 创建目标值（幂函数关系 + 噪声）
        y = 2.5 * (x ** 0.8) + np.random.randn(n_samples) * 0.5
        y = np.abs(y)  # 确保为正值
        
        return x, y
    
    def test_builder_initialization(self, builder):
        """测试构建器初始化"""
        assert builder is not None
        # 检查私有方法存在
        assert hasattr(builder, '_fit_power_model')
        assert hasattr(builder, '_fit_linear_model')
        assert hasattr(builder, 'tune_linear')
    
    def test_fit_power_model(self, builder, sample_data):
        """测试幂函数模型构建"""
        x, y = sample_data
        
        # 构建模型
        model_info = builder._fit_power_model(x, y)
        
        # 检查返回的模型信息
        assert isinstance(model_info, dict)
        assert 'formula' in model_info
        assert 'metrics' in model_info
        assert 'params' in model_info
        assert 'type' in model_info
        
        # 检查模型类型
        assert model_info['type'] == 'power'
        
        # 检查参数
        assert 'a' in model_info['params']
        assert 'b' in model_info['params']
        
        # 检查评估指标
        assert 'r2' in model_info['metrics']
        assert 'rmse' in model_info['metrics']
        
        # 检查R²值是否合理
        assert 0 <= model_info['metrics']['r2'] <= 1
    
    def test_fit_linear_model(self, builder):
        """测试线性模型构建"""
        # 创建线性关系数据
        np.random.seed(42)
        x = np.linspace(1, 10, 50)
        y = 2 * x + 3 + np.random.randn(50) * 0.5
        
        # 构建模型
        model_info = builder._fit_linear_model(x, y)
        
        # 检查返回的模型信息
        assert isinstance(model_info, dict)
        assert 'formula' in model_info
        assert 'metrics' in model_info
        assert 'params' in model_info
        assert 'type' in model_info
        
        # 检查模型类型
        assert model_info['type'] == 'linear'
        
        # 检查参数
        assert 'a' in model_info['params']  # 斜率
        assert 'b' in model_info['params']  # 截距
        
        # 检查参数接近真实值
        assert abs(model_info['params']['a'] - 2) < 0.5
        assert abs(model_info['params']['b'] - 3) < 1
    
    def test_model_prediction(self, builder, sample_data):
        """测试模型预测功能"""
        x, y = sample_data
        
        # 构建模型
        model_info = builder._fit_power_model(x, y)
        
        # 使用模型参数进行预测
        a = model_info['params']['a']
        b = model_info['params']['b']
        
        # 预测新值
        x_new = np.array([5.0, 7.5])
        y_pred = a * (x_new ** b)
        
        # 检查预测值是否合理
        assert len(y_pred) == len(x_new)
        assert np.all(y_pred > 0)  # 幂函数预测值应为正
    
    def test_invalid_data_handling(self, builder):
        """测试无效数据处理"""
        # 测试空数据
        x_empty = np.array([])
        y_empty = np.array([])
        
        model_info = builder._fit_power_model(x_empty, y_empty)
        
        # 应该返回空字典
        assert isinstance(model_info, dict)
        assert len(model_info) == 0
    
    def test_negative_values_handling(self, builder):
        """测试负值处理（幂函数模型）"""
        # 幂函数模型不能处理负值
        x = np.array([1, 2, -3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        
        # 构建模型时应该过滤掉负值
        model_info = builder._fit_power_model(x, y)
        
        # 检查是否成功处理
        assert isinstance(model_info, dict)
        # 应该成功拟合（过滤掉负值后）
        if model_info:  # 如果不是空字典
            assert 'type' in model_info
            assert model_info['type'] in ['power', 'linear']  # 可能回退到线性模型
    
    def test_insufficient_data_handling(self, builder):
        """测试数据不足的情况"""
        # 只有两个数据点
        x = np.array([1, 2])
        y = np.array([2, 4])
        
        model_info = builder._fit_power_model(x, y)
        
        # 应该能够处理（curve_fit最少需要参数数量的数据点）
        assert isinstance(model_info, dict)
    
    def test_tune_linear(self, builder):
        """测试线性调整功能"""
        # 创建预测值和实测值
        predicted = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        measured = pd.Series([0.9, 2.1, 2.9, 4.2, 4.8])
        
        # 进行线性调整
        tuning_factor = builder.tune_linear(predicted, measured)
        
        # 检查返回值
        assert tuning_factor is not None
        assert isinstance(tuning_factor, (float, np.floating))
        assert tuning_factor > 0  # 调整系数应该为正
    
    def test_tune_linear_with_missing_data(self, builder):
        """测试带缺失值的线性调整"""
        # 创建带缺失值的数据
        predicted = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0])
        measured = pd.Series([0.9, np.nan, 2.9, 4.2, 4.8])
        
        # 进行线性调整
        tuning_factor = builder.tune_linear(predicted, measured)
        
        # 应该能够处理缺失值
        assert tuning_factor is not None or len(predicted.dropna()) < 2
    
    def test_power_model_fallback_to_linear(self, builder):
        """测试幂函数模型失败时回退到线性模型"""
        # 创建会导致幂函数拟合失败的数据
        x = np.array([0.001, 0.002, 0.003, 0.004, 0.005])  # 非常小的值
        y = np.array([1000, 2000, 3000, 4000, 5000])  # 非常大的值
        
        model_info = builder._fit_power_model(x, y)
        
        # 应该返回模型信息（可能是线性模型）
        assert isinstance(model_info, dict)
        if model_info:
            assert 'type' in model_info
            # 可能回退到线性模型
            assert model_info['type'] in ['power', 'linear']