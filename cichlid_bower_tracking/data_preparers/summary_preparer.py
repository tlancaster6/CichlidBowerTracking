from matplotlib import (cm, colors, gridspec, ticker)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
import os
from types import SimpleNamespace
import sys
from sklearn.neighbors import KernelDensity
from skimage import morphology
from math import sqrt
import glob
import re

class SummaryPreparer:

    def __init__(self, FileManager):
        self.__version__ = '1.0.0'
        self.fm = FileManager
        self.da_obj = None
        self.ca_obj = None
        self.lp = None
        self.validateDepthData()
        self.validateClusterData()

    def validateDepthData(self):
        # Determine whether or not the required data for depth figures in present, and initiate a DepthAnalyzer
        # object if it is. Otherwise, return False

        # List out required files
        reqs = [self.fm.localLogfile,
                self.fm.localSummaryDir,
                self.fm.localSmoothDepthFile,
                self.fm.localTrayFile]

        # Check that each required file is present. If any file is missing, return False
        for path in reqs:
            if not os.path.exists(path):
                return False

        # If all required files were present, initiate the LogParser and DepthAnalyzer
        self.lp = self.fm.lp
        self.da_obj = DepthAnalyzer(self.fm)

    def validateClusterData(self):
        # Determine whether or not the required data for cluster figures in present, and initiate a ClusterAnalyzer
        # object if it is. Otherwise, return False

        # List out required files
        reqs = [self.fm.localLogfile,
                self.fm.localSummaryDir,
                self.fm.localAllLabeledClustersFile,
                self.fm.localTransMFile]

        # Check that each required file is present. If any file is missing, return False
        for path in reqs:
            if not os.path.exists(path):
                return False

        # If all required files were present, initiate the LogParser and ClusterAnalyzer
        self.lp = LP(self.fm.localLogfile)
        self.ca_obj = ClusterAnalyzer(self.fm)

    def createDepthFigures(self, hourlyDelta=2):
        # Create all figures based on depth data. Adjust hourlyDelta to influence the resolution of the
        # HourlyDepthSummary.pdf figure

        # Check that the DepthAnalzer object has been created, indicating that the required files are present.
        # Otherwise, skip creation of Depth Figures
        if self.da_obj is None:
            return

        # figures based on the depth data

        # Create summary figure of daily values
        figDaily = plt.figure(num=1, figsize=(11, 8.5))
        figDaily.suptitle(self.lp.projectID + ' Daily Depth Summary')
        gridDaily = gridspec.GridSpec(3, 1)

        # Create summary figure of hourly values
        figHourly = plt.figure(num=2, figsize=(11, 8.5))
        figHourly.suptitle(self.lp.projectID + ' Hourly Depth Summary')

        start_day = self.lp.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
        totalChangeData = vars(self.da_obj.returnVolumeSummary(self.lp.frames[0].time, self.lp.frames[-1].time))

        # Show picture of final depth
        topGrid = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gridDaily[0])
        topAx1 = figDaily.add_subplot(topGrid[0])
        topAx1_ax = topAx1.imshow(self.da_obj.returnHeight(self.lp.frames[-1].time, cropped=True), vmin=50, vmax=70)
        topAx1.set_title('Final Depth (cm)')
        topAx1.tick_params(colors=[0, 0, 0, 0])
        plt.colorbar(topAx1_ax, ax=topAx1)

        # Show picture of total depth change
        topAx2 = figDaily.add_subplot(topGrid[1])
        topAx2_ax = topAx2.imshow(self.da_obj.returnHeightChange(
            self.lp.frames[0].time, self.lp.frames[-1].time, cropped=True), vmin=-5, vmax=5)
        topAx2.set_title('Total Depth Change (cm)')
        topAx2.tick_params(colors=[0, 0, 0, 0])
        plt.colorbar(topAx2_ax, ax=topAx2)

        # Show picture of pit and castle mask
        topAx3 = figDaily.add_subplot(topGrid[2])
        topAx3_ax = topAx3.imshow(self.da_obj.returnHeightChange(self.lp.frames[0].time, self.lp.frames[-1].time, cropped = True, masked = True), vmin = -5, vmax = 5)
        topAx3.set_title('Masked Depth Change (cm)')
        topAx3.tick_params(colors=[0, 0, 0, 0])
        plt.colorbar(topAx3_ax, ax=topAx3)

        # Create figures and get data for daily Changes
        dailyChangeData = []
        w_ratios = ([1.0] * self.lp.numDays) + [0.25]
        midGrid = gridspec.GridSpecFromSubplotSpec(3, self.lp.numDays + 1, subplot_spec=gridDaily[1], width_ratios=w_ratios)
        v = 2
        for i in range(self.lp.numDays):
            start = start_day + datetime.timedelta(hours=24 * i)
            stop = start_day + datetime.timedelta(hours=24 * (i + 1))
            dailyChangeData.append(vars(self.da_obj.returnVolumeSummary(start, stop)))
            dailyChangeData[i]['Day'] = i + 1
            dailyChangeData[i]['Midpoint'] = i + 1 + .5
            dailyChangeData[i]['StartTime'] = str(start)

            current_axs = [figDaily.add_subplot(midGrid[n, i]) for n in [0, 1, 2]]
            current_axs[0].imshow(self.da_obj.returnHeightChange(start_day, stop, cropped=True), vmin=-v, vmax=v)
            current_axs[0].set_title('Day %i' % (i + 1))
            current_axs[1].imshow(self.da_obj.returnHeightChange(start, stop, cropped=True), vmin=-v, vmax=v)
            current_axs[2].imshow(self.da_obj.returnHeightChange(start, stop, masked=True, cropped=True), vmin=-v, vmax=v)
            [ax.tick_params(colors=[0, 0, 0, 0]) for ax in current_axs]
            [ax.set_adjustable('box') for ax in current_axs]
        cax = figDaily.add_subplot(midGrid[:, -1])
        plt.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-v, vmax=v), cmap='viridis'), cax=cax)

        figHourly = plt.figure(figsize=(11, 8.5))
        gridHourly = plt.GridSpec(self.lp.numDays, int(24 / hourlyDelta) + 2, wspace=0.05, hspace=0.05)
        bounding_ax = figHourly.add_subplot(gridHourly[:, :])
        bounding_ax.xaxis.set_visible(False)
        bounding_ax.set_ylabel('Day')
        bounding_ax.set_ylim(self.lp.numDays + 0.5, 0.5)
        bounding_ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1.0))
        bounding_ax.set_yticklabels(range(self.lp.numDays + 1))
        sns.despine(ax=bounding_ax, left=True, bottom=True)

        hourlyChangeData = []
        v = 1
        for i in range(0, self.lp.numDays):
            for j in range(int(24 / hourlyDelta)):
                start = start_day + datetime.timedelta(hours=24 * i + j * hourlyDelta)
                stop = start_day + datetime.timedelta(hours=24 * i + (j + 1) * hourlyDelta)

                hourlyChangeData.append(vars(self.da_obj.returnVolumeSummary(start, stop)))
                hourlyChangeData[-1]['Day'] = i + 1
                hourlyChangeData[-1]['Midpoint'] = i + 1 + ((j + 0.5) * hourlyDelta) / 24
                hourlyChangeData[-1]['StartTime'] = str(start)

                current_ax = figHourly.add_subplot(gridHourly[i, j])

                current_ax.imshow(self.da_obj.returnHeightChange(start, stop, cropped=True), vmin=-v, vmax=v)
                current_ax.set_adjustable('box')
                current_ax.tick_params(colors=[0, 0, 0, 0])
                if i == 0:
                    current_ax.set_title(str(j * hourlyDelta) + '-' + str((j + 1) * hourlyDelta))

            current_ax = figHourly.add_subplot(gridHourly[i, -2])
            current_ax.imshow(self.da_obj.returnBowerLocations(stop - datetime.timedelta(hours=24), stop, cropped=True),
                              vmin=-v, vmax=v)
            current_ax.set_adjustable('box')
            current_ax.tick_params(colors=[0, 0, 0, 0])
            if i == 0:
                current_ax.set_title('Daily\nMask')

            current_ax = figHourly.add_subplot(gridHourly[i, -1])
            current_ax.imshow(self.da_obj.returnHeightChange(stop - datetime.timedelta(hours=24), stop, cropped=True),
                              vmin=-v, vmax=v)
            current_ax.set_adjustable('box')
            current_ax.tick_params(colors=[0, 0, 0, 0])
            if i == 0:
                current_ax.set_title('Daily\nChange')

        totalDT = pd.DataFrame([totalChangeData])
        dailyDT = pd.DataFrame(dailyChangeData)
        hourlyDT = pd.DataFrame(hourlyChangeData)

        writer = pd.ExcelWriter(self.fm.localSummaryDir + 'DepthDataSummary.xlsx')
        totalDT.to_excel(writer, 'Total')
        dailyDT.to_excel(writer, 'Daily')
        hourlyDT.to_excel(writer, 'Hourly')
        writer.save()

        bottomGrid = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gridDaily[2], hspace=0.05)
        bIAx = figDaily.add_subplot(bottomGrid[1])
        bIAx.axhline(linewidth=1, alpha=0.5, y=0)
        bIAx.scatter(dailyDT['Midpoint'], dailyDT['bowerIndex'])
        bIAx.scatter(hourlyDT['Midpoint'], hourlyDT['bowerIndex'])
        bIAx.set_xlabel('Day')
        bIAx.set_ylabel('Bower\nIndex')
        bIAx.xaxis.set_major_locator(ticker.MultipleLocator(base=1.0))

        volAx = figDaily.add_subplot(bottomGrid[0], sharex=bIAx)
        volAx.plot(dailyDT['Midpoint'], dailyDT['bowerVolume'])
        volAx.plot(hourlyDT['Midpoint'], hourlyDT['bowerVolume'])
        volAx.set_ylabel('Volume\nChange')
        plt.setp(volAx.get_xticklabels(), visible=False)

        figDaily.savefig(self.fm.localSummaryDir + 'DailyDepthSummary.pdf')
        figHourly.savefig(self.fm.localSummaryDir + 'HourlyDepthSummary.pdf')

        plt.close('all')

    def createClusterFigures(self, hourlyDelta=1):
        # Create all figures based on Cluster data. Adjust hourlyDelta to influence the resolution of the
        # HourlyScoopSpitDensities.pdf figure

        # Check that the ClusterAnalyzer object has been created, indicating that the required files are present.
        # Otherwise, skip creation of Cluster Figures
        if self.ca_obj is None:
            return

        # figures based on the cluster data

        # semi-transparent scatterplots showing the spatial distrubtion of each cluster classification each day
        fig, axes = plt.subplots(10, self.lp.numDays, figsize=(8.5, 11))
        if self.lp.numDays == 1:
            axes = np.reshape(axes, (10, 1))
        fig.suptitle(self.lp.projectID + ' Daily Cluster Distributions')
        t0 = self.lp.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
        df_cropped = self.ca_obj.sliceDataframe(cropped=True)
        x_limits = (self.ca_obj.cropped_dims[0], 0)
        y_limits = (0, self.ca_obj.cropped_dims[1])
        for i in range(self.lp.numDays):
            t1 = t0 + datetime.timedelta(hours=24)
            df_slice = self.ca_obj.sliceDataframe(t0=t0, t1=t1, input_frame=df_cropped)
            for j, bid in enumerate(self.ca_obj.bids):
                df_slice_slice = self.ca_obj.sliceDataframe(input_frame=df_slice, bid=bid)
                sns.scatterplot(x='Y_depth', y='X_depth', data=df_slice_slice, ax=axes[j, i], s=10,
                                linewidth=0, alpha=0.1)
                axes[j, i].tick_params(colors=[0, 0, 0, 0])
                axes[j, i].set(xlabel=None, ylabel=None, aspect='equal', xlim=y_limits, ylim=x_limits)
                if j == 0:
                    axes[0, i].set_title('day %i' % (i + 1))
                if i == 0:
                    axes[j, 0].set_ylabel(str(bid))
            t0 = t1
        fig.savefig(self.fm.localSummaryDir + 'DailyClusterDistributions.pdf')
        plt.close(fig=fig)

        # heatmaps of the estimated daily scoop and spit areal densities
        start_day = self.lp.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
        fig, axes = plt.subplots(2, self.lp.numDays, figsize=(1.5 * self.lp.numDays, 4))
        if self.lp.numDays == 1:
            axes = np.reshape(axes, (2, 1))
        fig.suptitle(self.lp.projectID + ' Daily Scoop Spit Heatmaps')
        vmax = 0
        cbar_reference = None
        subplot_handles = []
        dailyChangeData = []
        for i in range(self.lp.numDays):
            start = start_day + datetime.timedelta(hours=24 * i)
            stop = start_day + datetime.timedelta(hours=24 * (i + 1))
            dailyChangeData.append(vars(self.da_obj.returnVolumeSummary(start, stop)))
            dailyChangeData[i]['Day'] = i + 1
            dailyChangeData[i]['Midpoint'] = i + 1 + .5
            dailyChangeData[i]['StartTime'] = str(start)

            z_scoop = self.ca_obj.returnClusterKDE(t0=start, t1=stop, bid='c', cropped=True)
            z_spit = self.ca_obj.returnClusterKDE(t0=start, t1=stop, bid='p', cropped=True)
            z = z_spit - z_scoop
            im = axes[0, i].imshow(z, cmap='viridis', interpolation='none')
            subplot_handles.append(im)
            axes[0, i].set(title='day %i' % (i + 1), xlabel=None, ylabel=None, aspect='equal')
            axes[0, i].tick_params(colors=[0, 0, 0, 0])
            if np.max(np.abs(z)) > vmax:
                vmax = np.max(np.abs(z))
                cbar_reference = im
            bowers = self.ca_obj.returnBowerLocations(start, stop, cropped=True)
            axes[1, i].imshow(bowers, cmap='viridis', vmin=-1, vmax=1)
            axes[1, i].set(xlabel=None, ylabel=None, aspect='equal')
            axes[1, i].tick_params(colors=[0, 0, 0, 0])
        for im in subplot_handles:
            im.set_clim(-vmax, vmax)
        if vmax != 0:
            cbar = fig.colorbar(cbar_reference, ax=axes[0, :].tolist(), shrink=0.7)
            cbar.set_label(r'$spits/cm^2$ - $scoops/cm^2$')
            cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
                         ax=axes[1, :].tolist(), shrink=0.7)
            cbar.set_label('bower region')
            cbar.set_ticks([-1, 0, 1])

        fig.savefig(self.fm.localSummaryDir + 'DailyScoopSpitDensities.pdf')
        plt.close(fig=fig)

        # heatmaps of the estimated hourly scoop and spit areal densities
        fig = plt.figure(figsize=(11, 8.5))
        grid = plt.GridSpec(self.lp.numDays, int(10 / hourlyDelta) + 2, wspace=0.05, hspace=0.05)
        bounding_ax = fig.add_subplot(grid[:, :])
        bounding_ax.xaxis.set_visible(False)
        bounding_ax.set_ylabel('Day')
        bounding_ax.set_ylim(self.lp.numDays + 0.5, 0.5)
        bounding_ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1.0))
        bounding_ax.set_yticklabels(range(self.lp.numDays + 1))
        sns.despine(ax=bounding_ax, left=True, bottom=True)

        hourlyChangeData = []
        v = 3
        for i in range(0, self.lp.numDays):
            for j in range(int(10 / hourlyDelta)):
                start = start_day + datetime.timedelta(hours=24 * i + j * hourlyDelta + 8)
                stop = start_day + datetime.timedelta(hours=24 * i + (j + 1) * hourlyDelta + 8)

                hourlyChangeData.append(vars(self.ca_obj.returnClusterSummary(start, stop)))
                hourlyChangeData[-1]['Day'] = i + 1
                hourlyChangeData[-1]['Midpoint'] = i + 1 + ((j + 0.5) * hourlyDelta + 8) / 24
                hourlyChangeData[-1]['StartTime'] = str(start)

                current_ax = fig.add_subplot(grid[i, j])

                scoops = self.ca_obj.returnClusterKDE(start, stop, 'c', cropped=True)
                spits = self.ca_obj.returnClusterKDE(start, stop, 'p', cropped=True)
                current_ax.imshow(spits - scoops, vmin=-v, vmax=v)
                current_ax.set_adjustable('box')
                current_ax.tick_params(colors=[0, 0, 0, 0])
                if i == 0:
                    current_ax.set_title(str(j * hourlyDelta + 8) + '-' + str((j + 1) * hourlyDelta + 8))

            current_ax = fig.add_subplot(grid[i, -2])
            current_ax.imshow(self.ca_obj.returnBowerLocations(stop - datetime.timedelta(hours=24), stop, cropped=True),
                              vmin=-1, vmax=1)
            current_ax.set_adjustable('box')
            current_ax.tick_params(colors=[0, 0, 0, 0])
            if i == 0:
                current_ax.set_title('Daily\nMask')

            current_ax = fig.add_subplot(grid[i, -1])
            scoops = self.ca_obj.returnClusterKDE(stop - datetime.timedelta(hours=24), stop, 'c', cropped=True)
            spits = self.ca_obj.returnClusterKDE(stop - datetime.timedelta(hours=24), stop, 'p', cropped=True)
            current_ax.imshow(spits - scoops, vmin=-v, vmax=v)
            current_ax.set_adjustable('box')
            current_ax.tick_params(colors=[0, 0, 0, 0])
            if i == 0:
                current_ax.set_title('Daily\nTotal')

        fig.savefig(self.fm.localSummaryDir + 'HourlyScoopSpitDensities.pdf')
        plt.close(fig=fig)

        totalChangeData = vars(self.ca_obj.returnClusterSummary(self.lp.frames[0].time, self.lp.frames[-1].time))

        totalDT = pd.DataFrame([totalChangeData])
        dailyDT = pd.DataFrame(dailyChangeData)
        hourlyDT = pd.DataFrame(hourlyChangeData)

        writer = pd.ExcelWriter(self.fm.localSummaryDir + 'ClusterDataSummary.xlsx')
        totalDT.to_excel(writer, 'Total')
        dailyDT.to_excel(writer, 'Daily')
        hourlyDT.to_excel(writer, 'Hourly')
        writer.save()

        # heatmap of the estimated whole-trial scoop and spit areal densities
        fig, ax = plt.subplots(1, 1)
        scoops = self.ca_obj.returnClusterKDE(self.lp.frames[0].time, self.lp.frames[-1].time, 'c', cropped=True)
        spits = self.ca_obj.returnClusterKDE(self.lp.frames[0].time, self.lp.frames[-1].time, 'p', cropped=True)
        z = spits - scoops
        v = 0.75 * np.max(np.abs(z))
        handle = ax.imshow(z, vmin=-v, vmax=v)
        cbar = fig.colorbar(handle, ax=ax)
        cbar.set_label(r'$spits/cm^2$ - $scoops/cm^2$')
        ax.set(title='whole-trial spit-scoop KDE', xlabel=None, ylabel=None, aspect='equal')
        ax.tick_params(colors=[0, 0, 0, 0])
        fig.savefig(self.fm.localSummaryDir + 'WholeTrialScoopSpitDensities.pdf')
        plt.close(fig=fig)

    def createCombinedFigures(self):
        # Create all figures that depend simultaneously on depth and cluster data.

        # Check that the ClusterAnalyzer object and DepthAnalyzer object have been created, indicating that the
        # required files are present. Otherwise, skip creation of Combined Figures
        if (self.ca_obj is None) or (self.da_obj is None):
            return

        # create figures based on a combination of cluster and depth data

        # plot overlap of daily bower regions identified from depth and cluster data
        fig, axes = plt.subplots(3, self.lp.numDays, figsize=(1.5 * self.lp.numDays, 6))
        if self.lp.numDays == 1:
            axes = np.reshape(axes, (3, 1))
        fig.suptitle(self.lp.projectID + ' Daily Bower Identification Consistency')
        t0 = self.lp.frames[0].time.replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(self.lp.numDays):
            t1 = t0 + datetime.timedelta(hours=24)

            depth_bowers = self.da_obj.returnBowerLocations(t0, t1, cropped=True)
            axes[0, i].imshow(depth_bowers, cmap='viridis', vmin=-1, vmax=1)
            axes[0, i].set(xlabel=None, ylabel=None, aspect='equal')
            axes[0, i].tick_params(colors=[0, 0, 0, 0])

            cluster_bowers = self.ca_obj.returnBowerLocations(t0, t1, cropped=True)
            axes[1, i].imshow(cluster_bowers, cmap='viridis', vmin=-1, vmax=1)
            axes[1, i].set(xlabel=None, ylabel=None, aspect='equal')
            axes[1, i].tick_params(colors=[0, 0, 0, 0])

            bower_intersection = np.where((depth_bowers == cluster_bowers) & (depth_bowers != 0), True, False)
            bower_intersection_area = np.count_nonzero(bower_intersection)
            bower_union = np.where((depth_bowers != 0) | (cluster_bowers != 0), True, False)
            bower_union_area = np.count_nonzero(bower_union)
            if bower_intersection_area == bower_union_area == 0:
                similarity = 1.0
            elif (bower_intersection_area == 0) | (bower_union_area == 0):
                similarity = 0.0
            else:
                similarity = bower_intersection_area / bower_union_area

            axes[2, i].imshow(-1 *((2 * bower_intersection) - bower_union), cmap='bwr', vmin=-1, vmax=1)
            axes[2, i].set(xlabel='J = {0:.3f}'.format(similarity), ylabel=None, aspect='equal')
            axes[2, i].tick_params(colors=[0, 0, 0, 0])

            t0 = t1

        axes[0, 0].set_ylabel('Depth Bowers')
        axes[1, 0].set_ylabel('Cluster Bowers')
        axes[2, 0].set_ylabel('Overlap')

        cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
                            ax=axes[0, :].tolist(), shrink=0.7)
        cbar.set_label('bower region')
        cbar.set_ticks([-1, 0, 1])
        cbar.set_ticklabels(['-', '0', '+'])

        cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
                            ax=axes[1, :].tolist(), shrink=0.7)
        cbar.set_label('bower region')
        cbar.set_ticks([-1, 0, 1])
        cbar.set_ticklabels(['-', '0', '+'])

        cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('bwr', 3)),
                            ax=axes[2, :].tolist(), shrink=0.7)
        cbar.set_label('Labels Agree?')
        cbar.set_ticks([-1, 1])
        cbar.set_ticklabels(['Y', 'N'])

        fig.savefig(self.fm.localSummaryDir + 'DailyBowerIdentificationConsistency.pdf')
        plt.close(fig=fig)

        # create figure of whole-trial bower identification overlap

        fig, axes = plt.subplots(3, 1, figsize=(2, 6))
        fig.suptitle(self.lp.projectID + ' Whole-Trial Bower Identification Consistency')
        t0 = self.lp.master_start.replace(hour=0, minute=0, second=0, microsecond=0)
        t1 = t0 + (self.lp.numDays * datetime.timedelta(hours=24))

        depth_bowers = self.da_obj.returnBowerLocations(t0, t1, cropped=True)
        axes[0].imshow(depth_bowers, cmap='viridis', vmin=-1, vmax=1)
        axes[0].set(xlabel=None, ylabel=None, aspect='equal')
        axes[0].tick_params(colors=[0, 0, 0, 0])

        cluster_bowers = self.ca_obj.returnBowerLocations(t0, t1, cropped=True)
        axes[1].imshow(cluster_bowers, cmap='viridis', vmin=-1, vmax=1)
        axes[1].set(xlabel=None, ylabel=None, aspect='equal')
        axes[1].tick_params(colors=[0, 0, 0, 0])

        bower_intersection = np.where((depth_bowers == cluster_bowers) & (depth_bowers != 0), True, False)
        bower_intersection_area = np.count_nonzero(bower_intersection)
        bower_union = np.where((depth_bowers != 0) | (cluster_bowers != 0), True, False)
        bower_union_area = np.count_nonzero(bower_union)
        if bower_intersection_area == bower_union_area == 0:
            similarity = 1.0
        elif (bower_intersection_area == 0) | (bower_union_area == 0):
            similarity = 0.0
        else:
            similarity = bower_intersection_area / bower_union_area

        axes[2].imshow(-1 *((2 * bower_intersection) - bower_union), cmap='bwr', vmin=-1, vmax=1)
        axes[2].set(xlabel='J = {0:.3f}'.format(similarity), ylabel=None, aspect='equal')
        axes[2].tick_params(colors=[0, 0, 0, 0])

        axes[0].set_ylabel('Depth Bowers')
        axes[1].set_ylabel('Cluster Bowers')
        axes[2].set_ylabel('Overlap')

        cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
                            ax=axes[0], shrink=0.7)
        cbar.set_label('bower region')
        cbar.set_ticks([-1, 0, 1])
        cbar.set_ticklabels(['-', '0', '+'])

        cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('viridis', 3)),
                            ax=axes[1], shrink=0.7)
        cbar.set_label('bower region')
        cbar.set_ticks([-1, 0, 1])
        cbar.set_ticklabels(['-', '0', '+'])

        cbar = fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin=-1, vmax=1), cmap=cm.get_cmap('bwr', 3)),
                            ax=axes[2], shrink=0.7)
        cbar.set_label('Labels Agree?')
        cbar.set_ticks([-1, 1])
        cbar.set_ticklabels(['Y', 'N'])

        fig.savefig(self.fm.localSummaryDir + 'WholeTrialBowerIdentificationConsistency.pdf')
        plt.close(fig=fig)

    def createPaceSummary(self):
        # if the troubleshooting directory contains .out files, uses them to summarize the PACE analysis. Otherwise,
        # print a message indicating that no .out files are present and move on.
        if os.path.exists(self.fm.localPaceDir) and len(glob.glob(str(self.fm.localPaceDir) + '*.out*')) > 0:
            regexes = {'job_id': re.compile(r'Job id:(?P<job_id>.*)\n'),
                       'job_name': re.compile(r'Job name:(?P<job_name>.*)\n'),
                       'requested': re.compile(r'Resources:(?P<requested>.*)\n'),
                       'used': re.compile(r'Rsrc Used:(?P<used>.*)\n'),
                       'start': re.compile(r'Begin PBS Prologue (?P<start>.*)\n'),
                       'end': re.compile(r'End PBS Epilogue (?P<end>.*)\n'),
                       'outcome': re.compile(r'PBS: job killed: (?P<outcome>.*)\n')}

            rows = []
            for f_name in glob.glob(str(self.fm.localPaceDir) + '*.out*'):
                row = {}
                with open(f_name) as f:
                    line = f.readline()
                    while line:
                        for key, rx in regexes.items():
                            match = rx.search(line)
                            if match:
                                if (key == 'requested') or (key == 'used'):
                                    update = [tuple([i.strip() for i in item.split('=', 1)])
                                              for item in re.split(r',|(?=.):(?=\D)', match.group(key))]
                                    update = [x + tuple('Y') if (len(x) is 1) else x for x in update]
                                    row.update(update)
                                else:
                                    row.update({key: match.group(key)})
                                if 'outcome' not in row.keys():
                                    row.update({'outcome': 'successful'})
                        line = f.readline()
                rows.append(row)
            all_data = pd.DataFrame(rows).sort_values(by='job_name').reset_index(drop=True)
            all_data.to_csv(self.fm.localSummaryDir + 'paceSummary.csv')

        else:
            print('no .out files in troubleshooting directory, skipping pace summary')

    def createFullSummary(self, clusterHourlyDelta=1, depthHourlyDelta=2):
        # Attempt to create all possible figures and summary files. If files required for a particular figure are
        # missing, it will be skipped without throwing an error. Adjust clusterHourlyDelta and depthHourlyDelta to
        # set the hourlyDelta argument of createDepthFigures and createClusterFigures respectively.
        self.createDepthFigures(hourlyDelta=depthHourlyDelta)
        self.createClusterFigures(hourlyDelta=clusterHourlyDelta)
        self.createCombinedFigures()
        self.createPaceSummary()

class DepthAnalyzer():
    # Contains code process depth data for figure creation

    def __init__(self, fileManager):
        self.fileManager = fileManager
        self.lp = LP(self.fileManager.localLogfile)
        self._loadData()
        self.goodPixels = (self.tray_r[2] - self.tray_r[0]) * (self.tray_r[3] - self.tray_r[1])

    def _loadData(self):
        # Loads depth tray information and smoothedDepthData from files that have already been downloaded

        # If tray attribute already exists, exit
        try:
            self.tray_r
        except AttributeError:
            with open(self.fileManager.localTrayFile) as f:
                line = next(f)
                tray = line.rstrip().split(',')
                self.tray_r = [int(x) for x in tray]

        try:
            self.smoothDepthData
        except AttributeError:
            self.smoothDepthData = np.load(self.fileManager.localSmoothDepthFile)
            self.smoothDepthData[:, :self.tray_r[0], :] = np.nan
            self.smoothDepthData[:, self.tray_r[2]:, :] = np.nan
            self.smoothDepthData[:, :, :self.tray_r[1]] = np.nan
            self.smoothDepthData[:, :, self.tray_r[3]:] = np.nan

    def returnBowerLocations(self, t0, t1, cropped=False):
        # Returns 2D numpy array using thresholding and minimum size data to identify bowers
        # Pits = -1, Castle = 1, No bower = 0

        # Check times are good
        self._checkTimes(t0, t1)

        # Identify total height change and time change
        totalHeightChange = self.returnHeightChange(t0, t1, masked=False, cropped=False)
        timeChange = t1 - t0

        # Determine threshold and minimum size of bower to use based upon timeChange
        if timeChange.total_seconds() < 7300:  # 2 hours or less
            totalThreshold = self.fileManager.hourlyDepthThreshold
            minPixels = self.fileManager.hourlyMinPixels
        elif timeChange.total_seconds() < 129600:  # 2 hours to 1.5 days
            totalThreshold = self.fileManager.dailyDepthThreshold
            minPixels = self.fileManager.dailyMinPixels
        else:  # 1.5 days or more
            totalThreshold = self.fileManager.totalDepthThreshold
            minPixels = self.fileManager.totalMinPixels

        tCastle = np.where(totalHeightChange >= totalThreshold, True, False)
        tCastle = morphology.remove_small_objects(tCastle, minPixels).astype(int)

        tPit = np.where(totalHeightChange <= -1 * totalThreshold, True, False)
        tPit = morphology.remove_small_objects(tPit, minPixels).astype(int)

        bowers = tCastle - tPit
        if cropped:
            bowers = bowers[self.tray_r[0]:self.tray_r[2], self.tray_r[1]:self.tray_r[3]]

        return bowers

    def returnHeight(self, t, cropped=False):
        # return the frame from the smoothedDepthData numpy closest to time t. If cropped is True, crop the frame
        # to include only the area defined by tray_r

        # Check times are good
        self._checkTimes(t)

        # Find closest frames to desired times
        try:
            first_index = max([False if x.time <= t else True for x in self.lp.frames].index(True) - 1,
                              0)  # This ensures that we get overnight changes when kinect wasn't running
        except ValueError:
            if t > self.lp.frames[-1].time:
                first_index = -1
            else:
                first_index = 0

        change = self.smoothDepthData[first_index]

        if cropped:
            change = change[self.tray_r[0]:self.tray_r[2], self.tray_r[1]:self.tray_r[3]]

        return change

    def returnHeightChange(self, t0, t1, masked=False, cropped=False):
        # return the height change, based on the smoothedDepthData numpy, from the frame closest to t0 to the frame
        # closest to t1. If cropped is True, crop the frame to include only the area defined by tray_r. If masked is
        # True, set the pixel value in all non-bower regions (see returnBowerLocations) to 0

        # Check times are good
        self._checkTimes(t0, t1)

        # Find closest frames to desired times
        try:
            first_index = max([False if x.time <= t0 else True for x in self.lp.frames].index(True) - 1,
                              0)  # This ensures that we get overnight changes when kinect wasn't running
        except ValueError:
            if t0 > self.lp.frames[-1].time:
                first_index = -1
            else:
                first_index = 0

        try:
            last_index = max([False if x.time <= t1 else True for x in self.lp.frames].index(True) - 1, 0)
        except ValueError:
            last_index = len(self.lp.frames) - 1

        change = self.smoothDepthData[first_index] - self.smoothDepthData[last_index]

        if masked:
            change[self.returnBowerLocations(t0, t1) == 0] = 0

        if cropped:
            change = change[self.tray_r[0]:self.tray_r[2], self.tray_r[1]:self.tray_r[3]]

        return change

    def returnVolumeSummary(self, t0, t1):
        # calculate various summary statistics for the depth change from t0 to t1

        # Check times are good
        self._checkTimes(t0, t1)

        pixelLength = self.fileManager.pixelLength
        bowerIndex_pixels = int(self.goodPixels * self.fileManager.bowerIndexFraction)

        bowerLocations = self.returnBowerLocations(t0, t1)
        heightChange = self.returnHeightChange(t0, t1)
        heightChangeAbs = heightChange.copy()
        heightChangeAbs = np.abs(heightChangeAbs)

        outData = SimpleNamespace()
        # Get data
        outData.projectID = self.lp.projectID
        outData.absoluteVolume = np.nansum(heightChangeAbs) * pixelLength ** 2
        outData.summedVolume = np.nansum(heightChange) * pixelLength ** 2
        outData.castleArea = np.count_nonzero(bowerLocations == 1) * pixelLength ** 2
        outData.pitArea = np.count_nonzero(bowerLocations == -1) * pixelLength ** 2
        outData.castleVolume = np.nansum(heightChange[bowerLocations == 1]) * pixelLength ** 2
        outData.pitVolume = np.nansum(heightChange[bowerLocations == -1]) * -1 * pixelLength ** 2
        outData.bowerVolume = outData.castleVolume + outData.pitVolume

        flattenedData = heightChangeAbs.flatten()
        sortedData = np.sort(flattenedData[~np.isnan(flattenedData)])
        threshold = sortedData[-1 * bowerIndex_pixels]
        thresholdCastleVolume = np.nansum(heightChangeAbs[(bowerLocations == 1) & (heightChangeAbs > threshold)])
        thresholdPitVolume = np.nansum(heightChangeAbs[(bowerLocations == -1) & (heightChangeAbs > threshold)])

        outData.bowerIndex = (thresholdCastleVolume - thresholdPitVolume) / (thresholdCastleVolume + thresholdPitVolume)

        return outData

    def _checkTimes(self, t0, t1=None):
        # validate the given times

        if t1 is None:
            if type(t0) != datetime.datetime:
                raise Exception('Timepoints to must be datetime.datetime objects')
            return
        # Make sure times are appropriate datetime objects
        if type(t0) != datetime.datetime or type(t1) != datetime.datetime:
            raise Exception('Timepoints to must be datetime.datetime objects')
        if t0 > t1:
            print('Warning: Second timepoint ' + str(t1) + ' is earlier than first timepoint ' + str(t0),
                  file=sys.stderr)


class ClusterAnalyzer:
    # Contains code process cluster data for figure creation
    def __init__(self, fileManager):
        self.fileManager = fileManager
        self.bids = ['c', 'p', 'b', 'f', 't', 'm', 's', 'd', 'o', 'x']
        self.lp = LP(fileManager.localLogfile)
        self._loadData()

    def _loadData(self):
        # load the required data

        self.transM = np.load(self.fileManager.localTransMFile)
        self.clusterData = pd.read_csv(self.fileManager.localAllLabeledClustersFile, index_col='TimeStamp',
                                       parse_dates=True, infer_datetime_format=True)
        self._appendDepthCoordinates()
        with open(self.fileManager.localTrayFile) as f:
            line = next(f)
            tray = line.rstrip().split(',')
            self.tray_r = [int(x) for x in tray]
        self.cropped_dims = [self.tray_r[2] - self.tray_r[0], self.tray_r[3] - self.tray_r[1]]
        self.goodPixels = (self.tray_r[2] - self.tray_r[0]) * (self.tray_r[3] - self.tray_r[1])

    def _appendDepthCoordinates(self):
        # adds columns containing X and Y in depth coordinates to all cluster csv
        self.clusterData['Y_depth'] = self.clusterData.apply(
            lambda row: (self.transM[0][0] * row.Y + self.transM[0][1] * row.X + self.transM[0][2]) / (
                    self.transM[2][0] * row.Y + self.transM[2][1] * row.X + self.transM[2][2]), axis=1)
        self.clusterData['X_depth'] = self.clusterData.apply(
            lambda row: (self.transM[1][0] * row.Y + self.transM[1][1] * row.X + self.transM[1][2]) / (
                    self.transM[2][0] * row.Y + self.transM[2][1] * row.X + self.transM[2][2]), axis=1)
        scaling_factor = sqrt(np.linalg.det(self.transM))
        self.clusterData['approx_radius'] = self.clusterData.apply(
            lambda row: (np.mean(row.X_span + row.Y_span) * scaling_factor)/2, axis=1)
        # self.clusterData.round({'X_Depth': 0, 'Y_Depth': 0})

        self.clusterData.to_csv(self.fileManager.localAllLabeledClustersFile)

    def sliceDataframe(self, t0=None, t1=None, bid=None, columns=None, input_frame=None, cropped=False):
        # utility function to access specific slices of the Dataframe based on the AllClusterData csv.
        #
        # t0: return only rows with timestamps after t0
        # t1: return only rows with timestamps before t1
        # bid: string or list of strings: return only rows for which the behavioral id matches the given string(s)
        # columns: list of strings: return only the columns of data matching the given keys
        # input_frame: pd.DataFrame: dataframe to slice from, instead of the default full dataframe.
        #              Allows for iterative slicing
        # cropped: If True, return only rows corresponding to events that occur within the area defined by tray_r

        df_slice = self.clusterData if input_frame is None else input_frame
        df_slice = df_slice.dropna(subset=['Model18_All_pred']).sort_index()
        if t0 is not None:
            self._checkTimes(t0, t1)
            df_slice = df_slice[t0:t1]
        if bid is not None:
            df_slice = df_slice[df_slice.Model18_All_pred.isin(bid if type(bid) is list else [bid])]
        if cropped:
            df_slice = df_slice[(df_slice.X_depth > self.tray_r[0]) & (df_slice.X_depth < self.tray_r[2]) &
                                (df_slice.Y_depth > self.tray_r[1]) & (df_slice.Y_depth < self.tray_r[3])]
            df_slice.X_depth = df_slice.X_depth - self.tray_r[0]
            df_slice.Y_depth = df_slice.Y_depth - self.tray_r[1]
        if columns is not None:
            df_slice = df_slice[columns]
        return df_slice

    def returnClusterCounts(self, t0, t1, bid='all', cropped=False):
        # return the number of behavioral events for a given behavior id (bid), or all bids, between t0 and t1
        #
        # t0: beginning of desired time frame
        # t1: end of desired time frame
        # bid: string or 'all': bid that will be counted. if a single bid is given, return counts (as an int) for that
        #      bid only. If 'all' (default behavior) return a dict of counts for all bids, keyed by bid.
        # cropped: If True, count only events occuring within the area defined by tray_r
        self._checkTimes(t0, t1)
        df_slice = self.sliceDataframe(cropped=cropped)
        if bid == 'all':
            df_slice = self.sliceDataframe(t0=t0, t1=t1, input_frame=df_slice)
            row = df_slice.Model18_All_pred.value_counts().to_dict
            return row
        else:
            df_slice = self.sliceDataframe(t0=t0, t1=t1, bid=bid, input_frame=df_slice)
            cell = df_slice.Model18_All_pred.count()
            return cell

    def returnClusterKDE(self, t0, t1, bid, cropped=False, bandwidth=None):
        # Geneate a kernel density estimate corresponding to the number events per cm^2 over a given timeframe for
        # a particular behavior id (bid)
        #
        # t0: beginning of time frame
        # t1: end of time frame
        # bid: string: generate a kde for this bid
        # cropped: if True, only include events within the area defined by tray_r
        # bandwidth: Can be used to manually set the kde bandwith (see sklearn.neighbors.KernelDensity). By default,
        #            use a bandwidth based on the average approximate event radius (see _appendDepthCoordinates)
        if bandwidth is None:
            bandwidth = self.sliceDataframe(t0, t1, bid, 'approx_radius').mean()/2
        df_slice = self.sliceDataframe(t0=t0, t1=t1, bid=bid, cropped=cropped, columns=['X_depth', 'Y_depth'])
        n_events = len(df_slice.index)
        x_bins = int(self.tray_r[2] - self.tray_r[0])
        y_bins = int(self.tray_r[3] - self.tray_r[1])
        xx, yy = np.mgrid[0:x_bins, 0:y_bins]
        if n_events == 0:
            z = np.zeros_like(xx)
        else:
            xy_sample = np.vstack([xx.ravel(), yy.ravel()]).T
            xy_train = df_slice.to_numpy()
            kde = KernelDensity(bandwidth=bandwidth, kernel='gaussian').fit(xy_train)
            z = np.exp(kde.score_samples(xy_sample)).reshape(xx.shape)
            z = (z * n_events) / (z.sum() * (self.fileManager.pixelLength ** 2))
        return z

    def returnBowerLocations(self, t0, t1, cropped=False, bandwidth=None):
        # Returns 2D numpy array using thresholding and minimum size data to identify bowers based on KDEs of spit and
        # scoop densities. Pits = -1, Castle = 1, No bower = 0
        #
        # t0: beginning of time frame
        # t1: end of time frame
        # cropped: if True, include in bower calculation only events within the area defined by tray_r
        # bandwith: see returnClusterKDE

        self._checkTimes(t0, t1)
        timeChange = t1 - t0

        if timeChange.total_seconds() < 7300:  # 2 hours or less
            totalThreshold = self.fileManager.hourlyClusterThreshold
            minPixels = self.fileManager.hourlyMinPixels
        elif timeChange.total_seconds() < 129600:  # 2 hours to 1.5 days
            totalThreshold = self.fileManager.dailyClusterThreshold
            minPixels = self.fileManager.dailyMinPixels
        else:  # 1.5 days or more
            totalThreshold = self.fileManager.totalClusterThreshold
            minPixels = self.fileManager.totalMinPixels

        z_scoop = self.returnClusterKDE(t0, t1, 'c', cropped=cropped, bandwidth=bandwidth)
        z_spit = self.returnClusterKDE(t0, t1, 'p', cropped=cropped, bandwidth=bandwidth)

        scoop_binary = np.where(z_spit - z_scoop <= -1 * totalThreshold, True, False)
        scoop_binary = morphology.remove_small_objects(scoop_binary, minPixels).astype(int)

        spit_binary = np.where(z_spit - z_scoop >= totalThreshold, True, False)
        spit_binary = morphology.remove_small_objects(spit_binary, minPixels).astype(int)

        bowers = spit_binary - scoop_binary
        return bowers

    def returnClusterSummary(self, t0, t1):
        # calculate various summary statistics for the scoop and spit KDEs from t0 to t1
        self._checkTimes(t0, t1)
        pixelLength = self.fileManager.pixelLength
        bowerIndex_pixels = int(self.goodPixels * self.fileManager.bowerIndexFraction)
        bowerLocations = self.returnBowerLocations(t0, t1)
        clusterKde = self.returnClusterKDE(t0, t1, 'p') - self.returnClusterKDE(t0, t1, 'c')
        clusterKdeAbs = clusterKde.copy()
        clusterKdeAbs = np.abs(clusterKdeAbs)

        outData = SimpleNamespace()
        # Get data
        outData.projectID = self.lp.projectID
        outData.absoluteKdeVolume = np.nansum(clusterKdeAbs) * pixelLength ** 2
        outData.summedKdeVolume = np.nansum(clusterKde) * pixelLength ** 2
        outData.castleArea = np.count_nonzero(bowerLocations == 1) * pixelLength ** 2
        outData.pitArea = np.count_nonzero(bowerLocations == -1) * pixelLength ** 2
        outData.castleKdeVolume = np.nansum(clusterKde[bowerLocations == 1]) * pixelLength ** 2
        outData.pitKdeVolume = np.nansum(clusterKde[bowerLocations == -1]) * -1 * pixelLength ** 2
        outData.bowerKdeVolume = outData.castleKdeVolume + outData.pitKdeVolume

        flattenedData = clusterKdeAbs.flatten()
        sortedData = np.sort(flattenedData[~np.isnan(flattenedData)])
        try:
            threshold = sortedData[-1 * bowerIndex_pixels]
        except IndexError:
            threshold = 0
        thresholdCastleKdeVolume = np.nansum(clusterKdeAbs[(bowerLocations == 1) & (clusterKdeAbs > threshold)])
        thresholdPitKdeVolume = np.nansum(clusterKdeAbs[(bowerLocations == -1) & (clusterKdeAbs > threshold)])

        outData.bowerIndex = (thresholdCastleKdeVolume - thresholdPitKdeVolume) / (thresholdCastleKdeVolume + thresholdPitKdeVolume)

        return outData

    def _checkTimes(self, t0, t1=None):
        # validate the given times
        if t1 is None:
            if type(t0) != datetime.datetime:
                raise Exception('Timepoints to must be datetime.datetime objects')
            return
        # Make sure times are appropriate datetime objects
        if type(t0) != datetime.datetime or type(t1) != datetime.datetime:
            raise Exception('Timepoints to must be datetime.datetime objects')
        if t0 > t1:
            print('Warning: Second timepoint ' + str(t1) + ' is earlier than first timepoint ' + str(t0),
                  file=sys.stderr)
