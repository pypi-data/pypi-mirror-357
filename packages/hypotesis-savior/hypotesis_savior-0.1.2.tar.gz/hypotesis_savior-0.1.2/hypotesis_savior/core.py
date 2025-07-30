from scipy.stats import levene
from scipy.stats import ttest_ind
from statsmodels.stats.weightstats import ztest
from scipy import stats
from scipy.stats import mannwhitneyu
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import itertools as it
import warnings
warnings.filterwarnings("ignore")

# форматирование текста
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

print(color.BOLD + 'Hello, World!' + color.END)

def diff(a, b, calculation_method='mean', percentile=90):
    if calculation_method == 'mean':
        absolute_diff = (np.mean(b) - np.mean(a))
        relative_diff = (np.mean(b) - np.mean(a)) / np.mean(a)
    elif calculation_method == 'median':
        absolute_diff = (np.median(b) - np.median(a))
        relative_diff = (np.median(b) - np.median(a)) / np.median(a)
    elif calculation_method == 'percentile':
        absolute_diff = (np.percentile(b, percentile) - np.percentile(a, percentile))
        relative_diff = (np.percentile(b, percentile) - np.percentile(a, percentile)) / np.percentile(a, percentile)
    else:
        raise Exception('Неизвестный метод оценки эффекта. Можно выбрать "mean", "median" или "percentile".')
    return absolute_diff, relative_diff


def stat_test(a, b, test='ttest', alpha=0.05):
    if test in ['ttest', 't test', 't-test', 't', 'student']:
        test_name = 't-test'
        if levene(a,b)[1] > alpha:
            stat, p_value = ttest_ind(a, b, equal_var=True)
        else:
            stat, p_value = ttest_ind(a, b, equal_var=False)
    elif test in ['ztest', 'z-test', 'z test', 'z']:
        test_name = 'z-test'
        stat, p_value = ztest(a, b)
    elif test in ['mannwhitneyu', 'mw', 'MW', 'u-test', 'u test', 'utest', 'u']:
        test_name = 'mannwhitneyu'
        stat, p_value = mannwhitneyu(a, b)
    else:
        raise Exception('Неизвестный критерий. Можно выбрать "ttest", "ztest" или "mannwhitneyu".')
    return stat, p_value, test_name


def relative_ttest(a, b, alpha=0.05):
  pass


def ztest(a, b):
    if ((a==0) | (a==1)).all():
        z_stat, p_value = ztest(a, b)
    else:
        raise Exception('z-test подходит только для бинарных данных')
    return z_stat, p_value


def mannwhitney():
    mw_stat, p_value = mannwhitneyu(a, b)
    return mw_stat, p_value


def bootstrap(a, b, n_iter, calculation_method='mean', percentile=90, alpha=0.05):
    bootstrap_diffs = []
    for _ in range(n_iter):
        control_sample = np.random.choice(a, size=len(a), replace=True)
        test_sample = np.random.choice(b, size=len(b), replace=True)
        bootstrap_diffs.append(diff(control_sample, test_sample, calculation_method, percentile)[1])
    ci_lower = np.percentile(bootstrap_diffs, 100 * alpha / 2)
    ci_upper = np.percentile(bootstrap_diffs, 100 * (1 - alpha / 2))
    is_significant = not (ci_lower <= 0 <= ci_upper)
    return 'bootstrap', ci_lower, ci_upper, is_significant

np.set_printoptions(legacy='1.25')

def run_stat_test(a, b, test='ttest', alpha=0.05, n_iter=1000, calculation_method='mean', percentile=90):
    stat_tests_names = ['ttest', 't test', 't-test', 't', 'student', 'ztest', 'z-test', 'z test', 'z', 'mannwhitneyu', 'mw', 'MW', 'u-test', 'u test', 'utest', 'u']
    
    if test in stat_tests_names and calculation_method == 'mean':
        stat, p_value, test_name = stat_test(a, b, test)
        ci_lower = None
        ci_upper = None
        is_significant = True if p_value < alpha else False
        return p_value, stat, test_name, ci_lower, ci_upper, is_significant

    elif test in stat_tests_names and calculation_method != 'mean':
        raise Exception('\nМедианы и перцентили нужно оценивать с помощью bootstrap')

    elif test == 'bootstrap':
        test_name, ci_lower, ci_upper, is_significant = bootstrap(a, b, n_iter, calculation_method='mean', percentile=90, alpha=0.05)
        p_value = None
        stat = None
        return p_value, stat, test_name, ci_lower, ci_upper, is_significant
    else:
        raise Exception('\nНеизвестный метод оценки гипотезы \nМожно выбрать "ttest", "ztest", "mannwhitneyu" или "bootstrap"')

def calc_strat_mean(df, strat_column, weights):
    strat_mean = df.groupby('strat')['metric'].mean()
    return (strat_mean * weights).sum()


def calc_strat_var(df, strat_column, weights):
    strat_var = df.groupby('strat')['metric'].var()
    return (strat_var * weights).sum()

def run_stratification(g1_df, g2_df, strat_column):
    weights = df[strat_column].value_counts(normalize=True).sort_index()

    g1_strat_mean = calc_strat_mean(g1_df, strat_column, weights)
    g2_strat_mean = calc_strat_mean(g2_df, strat_column, weights)
    g1_strat_var = calc_strat_var(g1_df, strat_column, weights)
    g2_strat_var = calc_strat_var(g2_df, strat_column, weights)

    delta = g2_strat_mean - g1_strat_mean
    rel_delta = (g2_strat_mean - g1_strat_mean) / g1_strat_mean
    std = (g1_strat_var / len(g1_df) + g2_strat_var / len(g2_df)) ** 0.5
    t = delta / std

    pvalue = 2 * (1 - stats.norm.cdf(np.abs(t)))
    return pvalue, delta, rel_delta

def cuped(a, a_pre, b, b_pre):
    a_corr = np.corrcoef(a_pre, a)[0, 1]
    b_corr = np.corrcoef(b_pre, b)[0, 1]

    a_theta = np.cov(a_pre, a)[0, 1] / np.var(a_pre)
    a_cuped = a - a_theta * (a_pre - np.mean(a_pre))

    b_theta = np.cov(b_pre, b)[0, 1] / np.var(b_pre)
    b_cuped = b - b_theta * (b_pre - np.mean(b_pre))
    return a_cuped, b_cuped, a_corr, b_corr

def bh_correction(pvalues, alpha=0.05):
    m = len(pvalues)
    alphas = alpha * np.arange(1, m+1) / m
    sorted_pvalue_indexes = np.argsort(pvalues)
    res = np.zeros(m, dtype=int)
    for alpha_, pvalue_index in zip(alphas, sorted_pvalue_indexes):
        pvalue = pvalues[pvalue_index]
        if pvalue <= alpha_:
            res[pvalue_index] = True
        else:
            res[pvalue_index] = False
    return res

def compute_dynamic_pvalue(df, groups=['control', 'test'], test='ttest', alpha=0.05, calculation_method='mean'):
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    unique_dates = np.sort(df['event_date'].unique())
    results = []

    for current_date in unique_dates:
        current_df = df.loc[df['event_date'] <= current_date].copy()

        control_data = current_df[current_df['group'] == groups[0]]['metric']
        test_data = current_df[current_df['group'] == groups[1]]['metric']

        if len(control_data) > 1 and len(test_data) > 1:
            res = run_stat_test(control_data, test_data, test=test, alpha=0.05, calculation_method='mean')
            pval = res[0]
        else:
            pval = np.nan
        results.append({
            'event_date': current_date,
            'pvalue': pval
        })
    return pd.DataFrame(results)

def compute_dynamic_metrics(df):
    df = df.copy()
    df['event_date'] = pd.to_datetime(df['event_date'])
    all_dates = pd.date_range(df['event_date'].min(), df['event_date'].max())
    groups = df['group'].unique()

    daily_data = []
    cumulative_data = []

    for current_date in all_dates:
        for group in groups:
            current_users = df[(df['group'] == group) & (df['event_date'] <= current_date)]
            # day metric
            day_metric = current_users[current_users['event_date'] == current_date]['metric'].sum()
            daily_data.append({'event_date': current_date, 'group': group, 'metric': day_metric})
            # cumulative metric
            cumulative_metric = current_users[current_users['event_date'] <= current_date]['metric'].sum()
            cumulative_data.append({'event_date': current_date, 'group': group, 'metric': cumulative_metric})

    daily_df = pd.DataFrame(daily_data)
    cumulative_df = pd.DataFrame(cumulative_data)
    
    return daily_df, cumulative_df

def run_analysis(df, df_predperiod=None, test='ttest', groups=['control', 'test'], alpha=0.05, n_iter=1000, calculation_method='mean', percentile=90, multiple_correction=False, strat_column=None, visualize=True):

    classic_test_results = {}
    cuped_results = {}
    stratification_results = {}
    corrs = {}
    has_low_corr = 0
    # groups = df['group'].unique()
    combs = it.combinations(groups, 2)
    combs_count = sum(1 for i in it.combinations(groups, 2))
    
    # задаем сабплоты
    if visualize==True:
        fig, axes = plt.subplots(1, combs_count, figsize=(5*len(groups), 5), sharey=True)
        if test != 'bootstrap':
            fig_p, axes_p = plt.subplots(1, combs_count, figsize=(5*len(groups), 5), sharey=True)
        fig_dm, axes_dm = plt.subplots(1, combs_count, figsize=(5*len(groups), 5), sharey=True)
        fig_cm, axes_cm = plt.subplots(1, combs_count, figsize=(5*len(groups), 5), sharey=True)
    
        if combs_count==1:
            axes = [axes]
            if test != 'bootstrap':
                axes_p = [axes_p]
            axes_dm = [axes_dm]
            axes_cm = [axes_cm]
            
    print(color.BOLD + '\nХарактеристики групп:' + color.END)
    user_metric = pd.DataFrame(df.groupby(['group','user_id'])['metric'].max())
    aggregates = user_metric.groupby('group')['metric'].agg(['min', 'max', 'mean', 'median', 'count']).reset_index()
    display(aggregates.rename(columns={'count': 'users_count'}))
    
    # для каждой пары групп проводим сравнение (на случай если в тесте больше 2 групп)
    for i, (g1, g2) in enumerate(combs):

        g1_metric = df[df.group==g1].metric
        g2_metric = df[df.group==g2].metric

        absolute_diff, relative_diff = diff(g1_metric, g2_metric, calculation_method, percentile)[0], diff(g1_metric, g2_metric, calculation_method, percentile)[1]

        # классический тест
        p_value, stat, test_name, ci_lower, ci_upper, is_sifnificant = run_stat_test(g1_metric, g2_metric, test, alpha, n_iter, calculation_method, percentile)
        if test_name == 'bootstrap':
            classic_test_results[f'{g1} vs {g2}'] = {'absolute_diff': absolute_diff, 'relative_diff': relative_diff, 'test_name': test_name, 'ci_lower': ci_lower, 'ci_upper': ci_upper, 'significance': is_sifnificant}
        else:
            classic_test_results[f'{g1} vs {g2}'] = {'absolute_diff': absolute_diff, 'relative_diff': relative_diff, 'test_name': test_name,'p_value': p_value}

        # cuped
        if df_predperiod is not None:

            g1_metric_predperiod = df_predperiod[df.group==g1].metric
            g2_metric_predperiod = df_predperiod[df.group==g2].metric
            g1_cuped, g2_cuped, g1_corr, g2_corr = cuped(g1_metric,
                                                     g1_metric_predperiod,
                                                     g2_metric,
                                                     g2_metric_predperiod,)

            p_value, stat, test_name, ci_lower, ci_upper, is_sifnificant = run_stat_test(g1_cuped, g2_cuped, test, alpha, n_iter, calculation_method, percentile)
            if test_name == 'bootstrap':
                cuped_results[f'[cuped] {g1} vs {g2}'] = {'absolute_diff': absolute_diff, 'relative_diff': relative_diff, 'test_name': test_name, 'ci_lower': ci_lower, 'ci_upper': ci_upper, 'significance': is_sifnificant}
            else:
                cuped_results[f'[cuped] {g1} vs {g2}'] = {'absolute_diff': absolute_diff, 'relative_diff': relative_diff, 'test_name': test_name,'p_value': p_value}
            
            for g_corr, g in zip([g1_corr, g2_corr], [g1, g2]):
                corrs[g] = g_corr
                if g_corr < 0.1:
                    has_low_corr = 1

        # стратификация
        if strat_column is not None:
            g1_df = df[df.group==g1][['metric', 'strat']]
            g2_df = df[df.group==g2][['metric', 'strat']]
            p_value, stat, test_name, ci_lower, ci_upper, is_sifnificant = run_stat_test(g1_metric, g2_metric, test, alpha, n_iter, calculation_method, percentile)
            p_value_strat, absolute_diff, relative_diff = run_stratification(g1_df, g2_df, strat_column)
            if test_name == 'bootstrap':
                stratification_results[f'[stratified] {g1} vs {g2}'] = {'absolute_diff': absolute_diff, 'relative_diff': relative_diff, 'test_name': test_name, 'ci_lower': ci_lower, 'ci_upper': ci_upper, 'significance': is_sifnificant}
            else:
                stratification_results[f'[stratified] {g1} vs {g2}'] = {'absolute_diff': absolute_diff, 'relative_diff': relative_diff, 'test_name': test_name,'p_value': p_value}
        else:
            pass

        # визуализация распределений
        if visualize==True:
            ax = axes[i]
            subset = df[df['group'].isin([g1, g2])]
            data1 = subset[subset['group'] == g1]['metric']
            data2 = subset[subset['group'] == g2]['metric']

            ax.hist(data1, bins=50, alpha=0.5, label=g1)
            ax.hist(data2, bins=50, alpha=0.5, label=g2)
            ax.set_title(f'{g1} vs {g2}')
            ax.legend()

            # визуализация p-value в динамике (пока только для расчета средних через стат тесты)
            df_comb = df[df['group'].isin([g1, g2])]
            if test != 'bootstrap':
                pvalues = compute_dynamic_pvalue(df=df_comb, groups=[g1, g2], test=test, alpha=alpha, calculation_method=calculation_method)
                ax_p = axes_p[i]
                ax_p.plot(pvalues['event_date'], pvalues['pvalue'])
                ax_p.tick_params(labelsize=8, labelrotation=45)
                ax_p.set_title(f'p-value: {g1} vs {g2}')

            # визуализация метрик по группам в динамике
            daily_metric, cumulative_metric = compute_dynamic_metrics(df_comb)
            ax_dm = axes_dm[i]
            ax_dm.plot(daily_metric[daily_metric['group']==g1]['event_date'], daily_metric[daily_metric['group']==g1]['metric'])
            ax_dm.plot(daily_metric[daily_metric['group']==g2]['event_date'], daily_metric[daily_metric['group']==g2]['metric'])
            ax_dm.tick_params(labelsize=8, labelrotation=45)
            ax_dm.set_title(f'daily metric')
            ax_dm.legend([g1, g2])
    
            ax_cm = axes_cm[i]
            ax_cm.plot(cumulative_metric[cumulative_metric['group']==g1]['event_date'], cumulative_metric[cumulative_metric['group']==g1]['metric'])
            ax_cm.plot(cumulative_metric[cumulative_metric['group']==g2]['event_date'], cumulative_metric[cumulative_metric['group']==g2]['metric'])
            ax_cm.tick_params(labelsize=8, labelrotation=45)
            ax_cm.set_title(f'cumulative metric')
            ax_cm.legend([g1, g2])

    all_results = []
    for results in [classic_test_results, cuped_results, stratification_results]:
        if len(results) != 0:
            df_results = pd.DataFrame(results).T
            if multiple_correction == True:
                if test == 'bootstrap':
                    pass
                else:
                    df_results['significance_corrected'] = bh_correction(list(df_results['p_value']), alpha)
            
            # display(df_results)
            all_results.append(df_results)

            # if has_low_corr == 1 and 'cuped' in list(results.keys())[0]:
            #     print(color.BOLD + color.RED + f'Есть группы с плохой корреляцией с предпериодом!' + color.END)
            #     for k in corrs.keys():
            #       print(f'- {k}: корреляция = {round(corrs[k], 3)}')
            # print('\n')
    print(color.BOLD + '\nРезультаты сравнений:' + color.END)
    display(pd.concat(all_results))
    if has_low_corr == 1:
        print(color.BOLD + color.RED + f'CUPED может быть неэффективен: есть группы с плохой корреляцией с предпериодом!' + color.END)
        for k in corrs.keys():
          print(f'- {k}: корреляция = {round(corrs[k], 3)}')
    print('\n')