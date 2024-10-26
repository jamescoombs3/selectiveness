"""
Parents in Kent were unaware that other parts of the country don't have the 11+ !

This prompted a quick plot of the total number of school places, and grammar school places for each local
authority based on DfE data here:
https://explore-education-statistics.service.gov.uk/find-statistics/school-pupils-and-their-characteristics

"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

cols = ['time_period', 'la_name', 'sex_of_school_description', 'phase_type_grouping', 'type_of_establishment',
        'denomination', 'admissions_policy', 'urban_rural', 'academy_flag',
        'number_of_key_stage_3_pupils_years_7_to_9', 'number_of_key_stage_4_pupils_years_10_and_11']

# load ~163k rows covering all years from 2015/16 and all school types.
df = pd.read_csv('C:/_python/normal/data/spc_school_characteristics_.csv', usecols=cols)

# Filter records to select latest year and education phase "state funded secondary" (~3k remain).
df = df.loc[((df.time_period == df.time_period.max()) & (df.phase_type_grouping == 'State-funded secondary'))]

# The following filters remove double counted aggregate values.
df = df.loc[(
        (df.sex_of_school_description == 'Total') &
        (df.type_of_establishment == 'Total') &
        (df.denomination == 'Total') &
        (df.urban_rural == 'Total') &
        (df.academy_flag == 'Total')
)]

# Secondary schools often have sixth forms. To count *secondary* pupil numbers, add the KS3 & KS4 numbers
df['roll'] = df.number_of_key_stage_3_pupils_years_7_to_9 + df.number_of_key_stage_4_pupils_years_10_and_11

# Main dataframe now contains 151 counties' state funded secondary schools for a single year with four
# type of 'admissions_policy'. These types are Total, Non-selective, Selective and Unknown.
# Unknown are always non-selective (having extensively checked this before).

# check a single familiar county
check = df.loc[(df.la_name == 'Buckinghamshire')]
# Tidy up
check = check.drop(columns=['time_period', 'sex_of_school_description', 'phase_type_grouping',
                            'type_of_establishment', 'denomination', 'urban_rural', 'academy_flag',
                            'number_of_key_stage_3_pupils_years_7_to_9',
                            'number_of_key_stage_4_pupils_years_10_and_11'])

print(check.pivot_table(index='la_name', columns='admissions_policy', values='roll'))
sel = check.roll.values[1]
tot = check.roll.values[2]
print('CHECK:', sel, 'out of', tot, 'children in Bucks are in grammars. This is', sel/tot, 'of the total')

# PREP DATA for PLOTTING
# Seaborn normally prefers 'tall/long' data but this plot works by plotting both the total and then
# selective pupils on the same figure so the data needs to be transformed to a 'wide' format.
dfp = df.pivot_table(index='la_name', columns='admissions_policy', values='roll')
dfp = dfp.drop(columns=['Non-selective', 'Not applicable', 'Unknown'])
dfp = dfp.reset_index()
dfp.Selective = pd.to_numeric(dfp.Selective, errors='coerce').fillna(0).astype(np.int64)
dfp.Total = pd.to_numeric(dfp.Total, errors='coerce').fillna(0).astype(np.int64)
dfp = dfp.sort_values(['Selective', 'Total'], ascending=[False, False])
dfp['pct'] = dfp.Selective / dfp.Total

# Example from https://pythonbasics.org/seaborn-barplot/
f, ax = plt.subplots(figsize=(6, 45))
sns.set_color_codes('pastel')
sns.barplot(x='Total', y='la_name', data=dfp,
            label='Total pupils', color='b', edgecolor='w')
sns.set_color_codes('muted')
sns.barplot(x='Selective', y='la_name', data=dfp,
            label='Pupils in grammars', color='b', edgecolor='w')

plt.xlabel('Pupil Numbers (2023/24)')
plt.ylabel('Local Authority')

ax.legend(ncol=1, loc='lower right', fontsize=10)

sns.despine(left=True, bottom=True)
for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(6)

ax.legend(prop=dict(size=6))
plt.show()

f.savefig('C:/_python/normal/data/figure1-300dpi.png', format='png', dpi=300)
