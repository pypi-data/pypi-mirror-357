from main import BatteryDataManager
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import numpy as np
manager = BatteryDataManager(base='sy',wip_line=None,table_prefix='PW')
def get_features_from_cell_ids(cell_ids,need=False,remove_rework = False):
    cap_df = manager.get_data_by_cell_ids(cell_ids, ['CAP']) 
    if remove_rework:
        cap_rework_cells = cap_df[cap_df['cap_rework_num'] == 1].cell_id.unique()
        cap_df = cap_df.query('cell_id not in @cap_rework_cells')
    else:
        cap_data_sorted = cap_df.sort_values(['cell_id', 'cap_rework_num'])
        cap_df = cap_data_sorted.groupby('cell_id', as_index=False).tail(1).reset_index(drop=True)


    
    ort_curves = manager.get_curves_by_cell_ids(list(cap_df.cell_id.unique()),'CAP').sort_values(['cell_id','step_no','sequence_no'])

    curves_temp = []
    for _,c in ort_curves.groupby('cell_id'):
        curves_temp.append(manager.tool.select_nth_data(c))
    ort_curves = pd.concat(curves_temp)
    ort_curves['time'] = (ort_curves['datetime'] - ort_curves.groupby('cell_id')['datetime'].transform('min')).dt.total_seconds()

    def compute_stage_features(df_stage, stage_label):
        """
        对于给定阶段数据 df_stage，计算以下特征：
          - 持续时长 (duration): 最后时间与开始时间之差
          - 温度统计：中位数、均值、最大值-最小值（幅度/范围）
          - 温度梯度： (最后温度-开始温度) / 持续时长
          - 温度积分偏差： 数值积分 np.trapz(temperature-25, x=time)
          - 电压统计：均值、中位数
          - 电压斜率： (最后电压-开始电压) / 持续时长
          - 容量统计：均值、中位数，以及容量斜率
        """
        features = {}
        if df_stage.empty:
            features[stage_label + '_duration'] = np.nan
            features[stage_label + '_temperature_median'] = np.nan
            features[stage_label + '_temperature_mean'] = np.nan
            features[stage_label + '_temperature_range'] = np.nan
            features[stage_label + '_temperature_gradient'] = np.nan
            features[stage_label + '_temperature_integral'] = np.nan
            features[stage_label + '_voltage_median'] = np.nan
            features[stage_label + '_voltage_mean'] = np.nan
            features[stage_label + '_voltage_slope'] = np.nan
            features[stage_label + '_capacity_median'] = np.nan
            features[stage_label + '_capacity_mean'] = np.nan
            features[stage_label + '_capacity_slope'] = np.nan
            return features

        # 排序确保时间是有序的
        df_stage = df_stage.sort_values('time')
        t_start = df_stage['time'].iloc[0]
        t_end = df_stage['time'].iloc[-1]
        duration = t_end - t_start
        features[stage_label + '_duration'] = duration

        # 计算斜率（用第一条与最后一条数据）
        if duration != 0:
            voltage_slope = (df_stage['voltage'].iloc[-1] - df_stage['voltage'].iloc[0]) / duration
            temperature_gradient = (df_stage['temperature'].iloc[-1] - df_stage['temperature'].iloc[0]) / duration
            capacity_slope = (df_stage['capacity'].iloc[-1] - df_stage['capacity'].iloc[0]) / duration
        else:
            voltage_slope = np.nan
            temperature_gradient = np.nan
            capacity_slope = np.nan

        features[stage_label + '_voltage_slope'] = voltage_slope
        features[stage_label + '_temperature_gradient'] = temperature_gradient
        features[stage_label + '_capacity_slope'] = capacity_slope

        # 温度统计
        features[stage_label + '_temperature_median'] = df_stage['temperature'].median()
        features[stage_label + '_temperature_mean'] = df_stage['temperature'].mean()
        features[stage_label + '_temperature_range'] = df_stage['temperature'].max() - df_stage['temperature'].min()
        # 温度积分偏差（积分时扣除标准25°C）
        features[stage_label + '_temperature_integral'] = np.trapz(df_stage['temperature'] - 25, x=df_stage['time'])

        # 电压统计
        features[stage_label + '_voltage_median'] = df_stage['voltage'].median()
        features[stage_label + '_voltage_mean'] = df_stage['voltage'].mean()

        # 容量统计
        features[stage_label + '_capacity_median'] = df_stage['capacity'].median()
        features[stage_label + '_capacity_mean'] = df_stage['capacity'].mean()
        features[stage_label + '_capacity'] = df_stage['capacity'].abs().max()

        return features
    
    mannul_fea = {}
    grpd = ort_curves.groupby('cell_id')
    for cell_id, c in tqdm(grpd, desc="Processing cells"):
        feats = {}
        # 对于各阶段：S1, S2, S3, S4, S5, S7, S8，统一提取我们需要的特征
        for step in [1, 2, 3, 4, 5, 7, 8]:
            df_stage = c[c['step_no'] == step]
            stage_label = 's' + str(step)
            stage_feats = compute_stage_features(df_stage, stage_label)
            feats.update(stage_feats)

            # 对S5（0.45C放电阶段），增加额外特征：
            if step == 5 and (not df_stage.empty):
                # 温度从起始到结束的变化（直接差值，不除持续时间）
                feats['s5_temperature_up'] = df_stage['temperature'].iloc[-1] - df_stage['temperature'].iloc[0]
                # S5电压1%分位值
                feats['s5_voltage_1p'] = df_stage['voltage'].quantile(0.01)
                # S5温度中位数的平方
                s5_median_temp = df_stage['temperature'].median()
                feats['s5_temperature_median_square'] = s5_median_temp ** 2

        # 这里对于S2、S5、S7中已有的容量中位数，已经通过 compute_stage_features 计算
        mannul_fea[cell_id] = feats
    mannul_fea_data = pd.DataFrame.from_dict(mannul_fea, orient='index').reset_index().rename(columns={'index':'cell_id'})
    fsij = manager.get_data_by_cell_ids(mannul_fea_data['cell_id'].unique(), ['FIJ','SIJ'])[['cell_id','sij_weight_after_injection']]
    for_cp = manager.get_data_by_cell_ids(mannul_fea_data['cell_id'].unique(), ['FOR']).sort_values(['cell_id', 'for_rework_num']).groupby('cell_id', as_index=False).tail(1).reset_index(drop=True)[['cell_id','for_voltage_s2','for_capacity_s2']]
    final_df_man = pd.merge(mannul_fea_data,fsij,on='cell_id',how='left')
    final_df_man = pd.merge(final_df_man,for_cp,on='cell_id',how='left')
    return final_df_man



def get_features_from_cell_ids_lite(cell_ids,need=False,remove_rework = False):
    zz = ['s5_capacity', 's7_capacity', 's5_temperature_mean', 'sij_weight_after_injection', '间隔时间']
    cap_df = manager.get_data_by_cell_ids(cell_ids, ['CAP'])
    sij_df = manager.get_data_by_cell_ids(cell_ids, ['SIJ'])
    if remove_rework:
        cap_rework_cells = cap_df[cap_df['cap_rework_num'] == 1].cell_id.unique()
        cap_df = cap_df.query('cell_id not in @cap_rework_cells')
    else:
        cap_data_sorted = cap_df.sort_values(['cell_id', 'cap_rework_num'])
        cap_df = cap_data_sorted.groupby('cell_id', as_index=False).tail(1).reset_index(drop=True)
    final_df_man = pd.merge(cap_df,sij_df,on='cell_id',how='left')
    final_df_man['间隔时间'] = 14
    final_df_man.rename(columns={'cap_capacity_s5':'s5_capacity','cap_capacity_s7':'s7_capacity'})
    return final_df_man
    # final_df_man = final_df_man[['cell_id','cap_out_time','cap_in_time','cap_is_rework','cap_rework_num','cap_capacity_s5','cap_capacity_s7','sij_weight_after_injection']]