from main import BatteryDataManager
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import numpy as np
manager = BatteryDataManager(base='sy',wip_line=None,table_prefix='PW')

def get_clean_cell_ids(start_date='2025-04-01', end_date='2025-04-15'):
    cap_df = manager.get_data_by_date_range(start_date, end_date, ['CAP'])
    cap_rework_cells = cap_df[cap_df['cap_is_rework'] == 1].cell_id.unique()
    cap_df = cap_df.query('cell_id not in @cap_rework_cells')
    cap_data = manager.tool.remove_outliers(cap_data, ['cap_capacity_s2', 'cap_capacity_s3', 'cap_capacity_s5','cap_capacity_s7', 'cap_capacity_s9'], 5)
    return cap_data
def get_features_from_cell_ids(cell_ids,need_label=True):
    cap_curves = manager.get_curves_by_cell_ids(cell_ids, 'CAP', step_sequence_no=[1,5])
    grpd = cap_curves.groupby('cell_id')
    features = []
    for i,c in tqdm(grpd):
        c = c.query("step_no <= 5 and voltage <= 3450").sort_values(by='sequence_no')
        if len(c) > 2500: continue
        temprature_90 = c.tail(1)['temperature'].values[0]
        temprature_0 = c.head(1)['temperature'].values[0]
        capacity_90 = -c.tail(1)['capacity'].values[0]
        features.append([i,temprature_0,capacity_90,temprature_90])
    features = pd.DataFrame(features,columns=['cell_id','temprature_0','capacity_90','temprature_90'])
    if need_label:
        cap_df = manager.get_data_by_cell_ids(cell_ids, ['CAP'])
        cap_rework_cells = cap_df[cap_df['cap_is_rework'] == 1].cell_id.unique()
        cap_df = cap_df.query('cell_id not in @cap_rework_cells')
        features = pd.merge(features,cap_df[['cell_id','cap_discharge_capacity','cap_compensated_capacity']],on='cell_id',how='inner')
    else:
        return features
    
def model_train(ddd):
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    # -------------------------
    # 假设 ddd 已加载，例如：
    # ddd = pd.read_csv('your_data.csv')
    # -------------------------

    # -------------------------
    # 1. 基于日期的训练集和测试集划分
    # -------------------------
    # 假设最新的日期用来作为测试集
    test_day = ddd.cap_out_time_day.unique().max()
    train_set = ddd.query("cap_out_time_day != @test_day").copy()
    test_set = ddd.query("cap_out_time_day == @test_day").copy()

    # 从训练集和测试集中提取特征和目标变量
    features = ['temprature_0', 'capacity_90', 'temprature_90']
    target = 'cap_discharge_capacity'

    X_train = train_set[features].values
    y_train = train_set[target].values
    X_test = test_set[features].values
    y_test = test_set[target].values

    # -------------------------
    # 2. 数据标准化
    # -------------------------
    scaler_X = StandardScaler()
    X_train = scaler_X.fit_transform(X_train)
    X_test = scaler_X.transform(X_test)

    scaler_y = StandardScaler()
    # 对 y 先转换为二维数组，标准化后保持二维格式
    y_train = scaler_y.fit_transform(y_train.reshape(-1, 1))
    y_test = scaler_y.transform(y_test.reshape(-1, 1))

    # -------------------------
    # 3. 转换为 PyTorch 张量
    # -------------------------
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32)  # 形状 (n_samples, 1)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32)

    # -------------------------
    # 4. 设备管理（CPU or GPU）
    # -------------------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # -------------------------
    # 5. 构建 DataLoader
    # -------------------------
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

    # -------------------------
    # 6. 定义 MLP 模型
    # -------------------------
    class MLP(nn.Module):
        def __init__(self, input_size):
            super(MLP, self).__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, 32),
                nn.BatchNorm1d(32),
                nn.LeakyReLU(0.1),
                # nn.Dropout(0.2),
                
                nn.Linear(32, 16),
                nn.BatchNorm1d(16),
                nn.LeakyReLU(0.1),
                # nn.Dropout(0.2),
                
                nn.Linear(16, 1),

            )
            self._initialize_weights()

        def _initialize_weights(self):
            # 使用 Xavier 初始化所有 Linear 层的权重
            for m in self.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)
                    if m.bias is not None:
                        nn.init.zeros_(m.bias)

        def forward(self, x):
            return self.net(x)

    input_size = X_train.shape[1]
    model = MLP(input_size).to(device)

    # -------------------------
    # 7. 定义损失函数、优化器、学习率调度器
    # -------------------------
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=5, factor=0.5, verbose=True
    )

    # -------------------------
    # 8. Early Stopping 参数设置
    # -------------------------
    early_stopping_patience = 10
    best_loss = float('inf')
    trigger_times = 0
    best_model_state = None

    # -------------------------
    # 9. 模型训练
    # -------------------------
    epochs = 20
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        total_samples = 0

        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            optimizer.zero_grad()
            predictions = model(X_batch)
            loss = criterion(predictions, y_batch)
            loss.backward()
            optimizer.step()
            
            # 按样本数加权累计 loss
            batch_size = X_batch.size(0)
            epoch_loss += loss.item() * batch_size
            total_samples += batch_size

        epoch_loss /= total_samples
        scheduler.step(epoch_loss)
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss:.6f}")

        # Early Stopping 检查
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            trigger_times = 0
            best_model_state = model.state_dict()  # 保存最佳模型状态
        else:
            trigger_times += 1
            if trigger_times >= early_stopping_patience:
                print("Early stopping triggered.")
                break

    # 加载最佳模型（如果存在）
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
    else:
        print("Warning: No best model state was saved. Using current model state.")

    # -------------------------
    # 10. 模型评估
    # -------------------------
    model.eval()
    with torch.no_grad():
        test_predictions_tensor = model(X_test_tensor.to(device))
        test_predictions_std = test_predictions_tensor.cpu().numpy()
        y_test_std = y_test_tensor.cpu().numpy()

    # 反标准化预测结果（保持二维形状）
    test_predictions = scaler_y.inverse_transform(test_predictions_std)
    y_test_actual = scaler_y.inverse_transform(y_test_std)

    # 计算评价指标
    rmse = mean_squared_error(y_test_actual, test_predictions, squared=False)
    mae = mean_absolute_error(y_test_actual, test_predictions)
    print(f"\nTest RMSE: {rmse:.4f}")
    print(f"Test MAE: {mae:.4f}")


    
    # -------------------------
    # 11. 绘图可视化结果
    # -------------------------
    plt.figure(figsize=(12, 5))

    # 左图：真实值 vs 预测值
    plt.subplot(1, 2, 1)
    plt.scatter(y_test_actual, test_predictions, alpha=0.6, marker='o', facecolors='none', edgecolors='k', label="Predictions")
    plt.plot([y_test_actual.min(), y_test_actual.max()],
            [y_test_actual.min(), y_test_actual.max()],
            'r--', lw=2, label="Ideal Fit")
    plt.xlabel("True Values")
    plt.ylabel("Predicted Values")
    plt.title("True vs Predicted Values")
    plt.legend()
    plt.grid(True)

    # 右图：残差图
    residuals = test_predictions - y_test_actual
    plt.subplot(1, 2, 2)
    plt.scatter(y_test_actual, residuals, alpha=0.6, marker='o', facecolors='none', edgecolors='k')
    plt.axhline(0, color='r', linestyle='--', lw=2)
    plt.xlabel("True Values")
    plt.ylabel("Residuals")
    plt.title("Residual Plot")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    # -------------------------
    # 12. 将模型预测结果写回 ddd
    # -------------------------
    # 用 scaler_X 对 ddd 中所有数据的特征进行标准化
    X_all = ddd[features].values
    X_all = scaler_X.transform(X_all)
    X_all_tensor = torch.tensor(X_all, dtype=torch.float32).to(device)

    model.eval()
    with torch.no_grad():
        predictions_all_tensor = model(X_all_tensor)
        predictions_all_std = predictions_all_tensor.cpu().numpy()

    # 反标准化预测结果
    predictions_all = scaler_y.inverse_transform(predictions_all_std)

    # 将预测结果写入 DataFrame，新增列 'predicted_cap_discharge_capacity'
    ddd['predicted_cap_discharge_capacity'] = predictions_all.flatten()

    print("模型预测结果已写回 DataFrame 'ddd' 到列 'predicted_cap_discharge_capacity'.")