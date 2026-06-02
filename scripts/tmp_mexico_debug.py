from scripts import common_pipeline as cp

periods = cp.get_periods('mexico', 2018)
print('periods', periods)
raw = cp.load_period('mexico', periods[1], 2018)
raw = cp.apply_geography_filter('mexico', 2018, raw)
print('raw cols', list(raw.columns[:20]))
print('id in raw', 'id' in raw.columns)
print('raw shape', raw.shape)
core = cp.build_core('mexico', 2018, 1, raw)
print('core cols', list(core.columns))
print(core.head(1))
