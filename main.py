#IMPORTS

import pandas as pd
import numpy as np
import requests
import os
import matplotlib.pyplot as plt
from tabulate import tabulate 


#HELPER FUNCTIONS

def get_ranked(df, sort_column, sort_flag, num_rows):
    df = df.sort_values(sort_column, ascending=sort_flag).head(num_rows)
    df.reset_index(inplace=True, drop=True)
    return df

def print_table(table, keys='keys'):
    print(tabulate(table, headers=keys, tablefmt='fancy_outline'))

#PRELIMINARY PROCESSING

#input .csv file
input_file_name = 'U.S. Presidents Birth and Death Information - Sheet1.csv'
input_file_url = 'https://raw.githubusercontent.com/senrabc/a_problem_with_presidents/main/' + input_file_name

#output plot directory
output_plot = 'plots'

#check if file is available locally, else download it
if(not os.path.isfile(input_file_name)):
    res = requests.get(input_file_url)
    open(input_file_name, 'wb').write(res.content)

#check if plots/ directory exists, if not, create it
if(not os.path.isdir(output_plot)):
    os.makedirs((output_plot))

#WORKING WITH THE DATAFRAME

#create dataframe from input csv
df = pd.read_csv(input_file_name)

#remove 'References' row in the dataframe
df.drop(df.tail(1).index, inplace=True)

#Convert to convenient Datetime objects
df['cleanedDOB'] = pd.to_datetime(df['BIRTH DATE']) 
df['cleanedDOD'] = pd.to_datetime(df['DEATH DATE'])

#calculate year_of_birth
df['year_of_birth'] = df['cleanedDOB'].dt.year
#current day normalized to midnight 00:00:00
today = pd.Timestamp.now().normalize()
#calculate days lived
df['lived_days'] = (df['cleanedDOD'] - df['cleanedDOB']).where(df['cleanedDOD'].notnull(), other=today - df['cleanedDOB']).dt.days
#calculate years lived
df['lived_years'] = (df['lived_days'] / 365.25).astype(int)
#calculate months lived
df['months_lived'] = (df['lived_days'] / 12.0).astype(int)


#top 10 longest lived presidents
longest_lived = get_ranked(df, 'lived_days', False, 10)

#top 10 shortest lived presidents
shortest_lived = get_ranked(df, 'lived_days', True, 10)

#print top 10 presidents
columns_to_display = ['PRESIDENT', 'BIRTH DATE', 'DEATH DATE', 'lived_days']

print('Top 10 longest lived presidents')
print_table(longest_lived[columns_to_display])

print('Top 10 shortest lived presidents')
print_table(shortest_lived[columns_to_display])


#New dataframe for statistics
stats = pd.DataFrame()
#calculate mean
stats['mean'] = [df['lived_days'].mean()]
#calculate median
stats['median'] = [df['lived_days'].median()]
#calculate max value
stats['max'] = [df['lived_days'].max()]
#calculate min value
stats['min'] = [df['lived_days'].min()]
#calculate mode (using lived_years for sensible results)
stats['mode(years)'] = [df['lived_years'].mode().tolist()]

#constant weight for all values
std = df['lived_days'].std()
w_i = 1 / (std * std)
#calculate weighted average
w_avg = (df['lived_days'].sum() * w_i) / (w_i * df.shape[0])
#assign w_avg to appropriate column
stats['weighted avg.'] = [w_avg]

#print statistics table
print('Statistics')
print_table(stats.transpose(), '')


#PLOTTING
#pyplot configuration
plt.style.use('default')

#copy of stats dataframe
stt = stats.copy()
#we use first value in mode array and convert to days
stt['mode'] = stt['mode(years)'][0][0] * 365.25
#drop mode(years)
stt.drop('mode(years)', axis=1, inplace=True)

#plot statistics as a bar graph
plt.figure()
ax = stt.transpose().plot.bar(xlabel='Statistic', ylabel='Value (in days)',legend=None)
ax.set_xticklabels(ax.get_xticklabels(), rotation = 0)
plt.axhline(y=stt['mean'][0], color='r')
plt.legend(['Mean'])
plt.savefig('plots/Statistics.png')
plt.close()

#get frequencies of president ages (years)
plt.figure()
freq = df['lived_years'].value_counts()
freqmax = freq.max()
ax2 = freq.plot(kind='bar', xlabel='Age(years)', ylabel='No. of presidents')
ax2.set_yticks(range(0, freqmax + 1))
plt.savefig('plots/Age_Freq.png')
plt.close()

#plotting living vs dead presidents
plt.figure()
total_presidents = df.shape[0]
num_living = df['cleanedDOD'].isna().sum()
num_dead = total_presidents - num_living
ax3 = plt.bar(['Living', 'Dead'],[num_living, num_dead])
plt.xlabel('Status')
plt.ylabel('No. of presidents')
plt.savefig('plots/Status.png')
plt.close()















    
