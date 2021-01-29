import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.ticker as mtick

def remove_strange_data(input_df):
    # remove points that randomly spiked
    df = input_df.reset_index()
    s_diff_diff = (df.SEMIMAJOR_AXIS.diff()-df.SEMIMAJOR_AXIS.diff(-1)).abs()+1
    s_diff_sum = (df.SEMIMAJOR_AXIS.diff()+df.SEMIMAJOR_AXIS.diff(-1)).abs()
    i_diff_diff = (df.INCLINATION.diff()-df.INCLINATION.diff(-1)).abs()+1
    i_diff_sum = (df.INCLINATION.diff()+df.INCLINATION.diff(-1)).abs()
    # should return removed rows separately also
    return (df.loc[~(((s_diff_diff > 0) & (s_diff_sum / s_diff_diff > 1000)) | ((i_diff_diff > 0) & (i_diff_sum / i_diff_diff > 1000)))]).set_index("EPOCH")

def generate_event_ranges(all_maneuvered):
    df = pd.DataFrame(all_maneuvered)
    mdf = df.any(axis='columns')
    mdf.name = "maneuvered"
    mdf = mdf.to_frame()
    mdf['maneuvere_group'] = (mdf.maneuvered != mdf.maneuvered.shift())
    mdf['maneuvere_group'] = mdf['maneuvere_group'].fillna(False).astype(int).cumsum()
    grouped = mdf.reset_index().groupby('maneuvere_group')
    events = pd.DataFrame({'start' : grouped.EPOCH.first(),
                           'end' : grouped.EPOCH.last(),
                           'v' : grouped.maneuvered.first()}).reset_index(drop=True)
    events = events[events.v==True][['start','end']]
    day = pd.offsets.Day()
    events['start'] = events['start'] - day
    events['end'] = events['end'] + day
    events['group'] = (events.start >= events.end.shift()).cumsum()
    event_ranges = pd.DataFrame({'start' : events.groupby('group').start.first(),
                                 'end' : events.groupby('group').end.last()}).reset_index(drop=True)
    return event_ranges


def find_maneuvers(df, maneuver_functions):
    mdf = df.copy()
    all_ranges = {}
    all_maneuvered = {}
    for col, funcs in maneuver_functions.items():
        all_ranges[col] = []
        for name, func, thresholds in funcs:
            all_thresholds = []
            for threshold in thresholds:
                mdf['maneuvers'] = func(mdf[col])
                mdf['maneuvered'] = (mdf.maneuvers > threshold) | (mdf.maneuvers < -threshold)
                all_maneuvered[col+name] = mdf['maneuvered'].copy()
                event_ranges = generate_event_ranges({name:mdf['maneuvered']})
                all_thresholds.append((threshold, event_ranges))

            all_ranges[col].append((name, mdf[["maneuvers"]], all_thresholds))
    return all_ranges, generate_event_ranges(all_maneuvered)
    
def plot_maneuvers(df, maneuver_results, sat_name):
    cmap = matplotlib.cm.get_cmap('OrRd')
    num_col = len(maneuver_results)
    num_row = max([len(v) for v in maneuver_results.values()]) +1
    fig, ax = plt.subplots(num_row, num_col, sharex="col", squeeze=True, figsize=(15,num_row*3))

    for i,key in enumerate(maneuver_results):
        fig.suptitle(sat_name, fontsize=15)
        ax[0, i].set_title(key, fontsize=13)
        ax[0, i].set_xlim(df.index[0], df.index[-1])
        df[key].plot(ax=ax[0, i], label="_")
        ax[0, i].ticklabel_format(useOffset=False, style='plain',axis='y')
        for j, v in enumerate(maneuver_results[key]):
            ax[j+1, i].ticklabel_format(useOffset=False, style='plain',axis='y')
            name, maneuvers, thresholds_event_ranges = v
            
            thresholds, event_ranges = zip(*thresholds_event_ranges)
            ax[j+1, i].set_title(f'"{key} {name}" w/ threshold {thresholds}', fontsize=11)
            ax[j+1, i].set_xlim(df.index[0], df.index[-1])
            ax[j+1, i].set_ylim(-1.5*max(thresholds), 1.5*max(thresholds))

            maneuvers.dropna().plot(ax=ax[j+1, i], label="_", legend=False)
            xmin, xmax = ax[j+1, i].get_xlim()
            for k, threshold in enumerate(thresholds):
                ax[j+1, i].hlines([threshold, -threshold], xmin, xmax, color=cmap((k+1)/(len(thresholds)+2)), linewidth=1)
            for k, event_range in enumerate(event_ranges):
                for _,er in event_range.iterrows():
                    ax[j+1,i].axvspan(er.start, er.end, alpha=0.5, color=cmap((k+1)/(len(thresholds)+2)), label="_")
    return fig

def set_min_ylim(ax,v):
    sa1,sa2 = ax.get_ylim()
    if sa2-sa1 < v:
        sa = (sa1+sa2)/2
        ax.set_ylim(sa-v/2, sa+v/2)

def plot_combined_maneuvers(fig, ax, df, event_range, sat_name):
    fig.suptitle(sat_name, fontsize=15)
    ax.set_title("Maneuvers Detected", fontsize=13)
    ax.set_xlim(df.index[0], df.index[-1])
    df['SEMIMAJOR_AXIS'].plot(ax=ax, label="SEMIMAJOR_AXIS")
    # set ylim minimum: 0.1 inclination 0.2 semimajor
    ax2 = ax.twinx()
    df['INCLINATION'].plot(ax=ax2, color="#fc8215", label="INCLINATION")
    ax.set_ylabel("Semimajor Axis")
    ax2.set_ylabel("Inclination")
    ax.ticklabel_format(useOffset=False, style='plain',axis='y')
    ax2.ticklabel_format(useOffset=False, style='plain',axis='y')
    set_min_ylim(ax,0.2)
    set_min_ylim(ax2,0.1)
    for _,er in event_range.iterrows():
        ax.axvspan(er.start, er.end, alpha=0.5, color="#ffd2ae", label="_")
    
                    
def explore_maneuvers_thresholds(norad_id, df_slice, maneuver_functions):
    raw = df[df.NORAD_CAT_ID == norad_id][df_slice].copy()

    # revert back the scaling
    raw["SEMIMAJOR_AXIS"] = raw["SEMIMAJOR_AXIS_x1000"].astype(np.float64)/1000
    raw["INCLINATION"] = raw["INCLINATION_x10000"].astype(np.float64)/10000
    raw = raw.drop(columns=["SEMIMAJOR_AXIS_x1000","INCLINATION_x10000"])

    fixed = remove_strange_data(raw)

    maneuver_results, _ = find_maneuvers(fixed, maneuver_functions)

    stuff = (fixed, maneuver_results, f'{satcat.loc[(satcat.NORAD_CAT_ID == norad_id),"SATNAME"].values[0]} ({norad_id}) ')
    fig = plot_maneuvers(*stuff)
    fig.tight_layout(pad=1.5)
    fig.set_facecolor("white")
    return raw, fixed, maneuver_results, fig


                    
def plot_maneuver_results(df, satcat, norad_id, df_slice, maneuver_functions, combined=False):
    raw = df[df.NORAD_CAT_ID == norad_id][df_slice].copy()

    # revert back the scaling
    raw["SEMIMAJOR_AXIS"] = raw["SEMIMAJOR_AXIS_x1000"].astype(np.float64)/1000
    raw["INCLINATION"] = raw["INCLINATION_x10000"].astype(np.float64)/10000
    raw = raw.drop(columns=["SEMIMAJOR_AXIS_x1000","INCLINATION_x10000"])

    fixed = remove_strange_data(raw)

    maneuver_results, combined_results = find_maneuvers(fixed, maneuver_functions)

    if combined:
        stuff = (fixed, combined_results, f'{satcat.loc[(satcat.NORAD_CAT_ID == norad_id),"SATNAME"].values[0]} ({norad_id}) ')
        fig, ax = plt.subplots(squeeze=True, figsize=(15,7))
        plot_combined_maneuvers(fig, ax, *stuff)
        fig.tight_layout(pad=1.5)
        fig.set_facecolor("white")
        fig.legend()
        return raw, fixed, combined_results, fig
    else:
        stuff = (fixed, maneuver_results, f'{satcat.loc[(satcat.NORAD_CAT_ID == norad_id),"SATNAME"].values[0]} ({norad_id}) ')
        fig = plot_maneuvers(*stuff)
        fig.tight_layout(pad=1.5)
        fig.set_facecolor("white")
        return raw, fixed, maneuver_results, fig
    
    
def plot_extra_lines(ax, sat, probs, soc_data):
    for e in sat.index:
        ax.axvline(x=e, lw=1, c="#00000033")
    ax2 = ax.twinx()
    (probs*100).plot(ax=ax2, color="purple", legend=False)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.axvline(x=soc_data.extract_date.min(), lw=2, c="green")
    ax.axvline(x=soc_data.tca_time.mean(), lw=2, c="red")