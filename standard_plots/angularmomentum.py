
# ICRAR - International Centre for Radio Astronomy Research
# (c) UWA - The University of Western Australia, 2018
# Copyright by UWA (in the framework of the ICRAR)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Angular momentum plots"""

import functools

import numpy as np

import common
import utilities_statistics as us

# Initialize arguments
zlist = ["199","174", "156", "131"]

##################################
#Constants
RExp     = 1.67
MpcToKpc = 1e3
G        = 4.299e-9 #Gravity constant in units of (km/s)^2 * Mpc/Msun

#stellar mass bins
mlow = 6.5
mupp = 12.5
dm = 0.2
mbins = np.arange(mlow,mupp,dm)
xmf = mbins + dm/2.0

#DM bins
mlowh = 10.0
mupph = 15.0
mbinsh = np.arange(mlowh,mupph,dm)
xmfh   = mbinsh + dm/2.0

dmobs = 0.4
mbins_obs = np.arange(mlow,mupp,dmobs)
xmf_obs = mbins_obs + dmobs/2.0

llow = -3.0
lupp = 2.0
dl   = 0.15
lbins = np.arange(llow,lupp,dl)
xlf   = lbins + dl/2.0


def prepare_data(hdf5_data, index, sam_stars_disk, sam_gas_disk_atom, sam_gas_disk_mol, sam_halo, sam_ratio_halo_disk, sam_ratio_halo_gal, sam_ratio_halo_disk_gas):

    (h0, _, mdisk, mbulge, mburst_mergers, mburst_diskins, mstars_bulge_mergers_assembly, mstars_bulge_diskins_assembly, 
     mBH, rdisk, rbulge, typeg, specific_angular_momentum_disk_star, specific_angular_momentum_bulge_star, 
     specific_angular_momentum_disk_gas, specific_angular_momentum_bulge_gas, specific_angular_momentum_disk_gas_atom, 
     specific_angular_momentum_disk_gas_mol, lambda_sub, mvir_s, mvir, matom_disk, mmol_disk, mgas_disk,
     matom_bulge, mmol_bulge, mgas_bulge) = hdf5_data

    mbulge_mergers = mburst_mergers + mstars_bulge_mergers_assembly
    zero_bulge = np.where(rbulge <= 0)
    if(len(rbulge) == len(rbulge[zero_bulge])):
            #case where there is zero bulge build up.
            rbulge[zero_bulge] = 1e-10
            specific_angular_momentum_bulge_star[zero_bulge] = 1.0
            mbulge[zero_bulge] = 10.0

    bin_it = functools.partial(us.wmedians, xbins=xmf, low_numbers=True)
    bin_it_halo = functools.partial(us.wmedians, xbins=xmfh, low_numbers=True)

    sam_subhalo = 1.41421356237 * G**0.66 * lambda_sub * mvir_s**0.66 / (h0*100.0)**0.33
    sam_hhalo   = 1.41421356237 * G**0.66 * lambda_sub * mvir**0.66 / (h0*100.0)**0.33

    specific_angular_momentum_disk = (specific_angular_momentum_disk_star * mdisk + specific_angular_momentum_disk_gas * mgas_disk) / (mdisk + mgas_disk)

    lh = lambda_sub
    ls = specific_angular_momentum_disk / 1.41421356237 / G**0.66 / (mdisk + mgas_disk)**0.66 * (h0*100.0)**0.33

    bt = np.zeros(shape = (len(mdisk)))
    ms = np.zeros(shape = (len(mdisk)))
    ind = np.where(mdisk+mbulge > 0) 
    bt[ind] = mbulge[ind] / (mdisk[ind] + mbulge[ind])
    ms[ind] = np.log10(mdisk[ind] + mbulge[ind])

    #calculate effective specific angular momentum by mass-weighting the contributions from the disk and bulge
    sam_stars   = (specific_angular_momentum_disk_star * mdisk + specific_angular_momentum_bulge_star * mbulge) / (mdisk+mbulge)
    

    vdisk  = specific_angular_momentum_disk_star / rdisk / 2.0 #in km/s
    vbulge = specific_angular_momentum_bulge_star / rbulge / 2.0 #in km/s
   
    ind = np.where((specific_angular_momentum_disk_star > 0) & (mdisk+mbulge > 0) & (mbulge/(mdisk+mbulge) < 0.5) & (typeg == 0))
    sam_stars_disk[index,:]   = bin_it(x=np.log10(mdisk[ind]+mbulge[ind]) - np.log10(float(h0)),
                                       y=np.log10(sam_stars[ind]) - np.log10(float(h0))) #specific_angular_momentum_disk_star[ind]) - np.log10(float(h0)))
    ind = np.where((sam_stars > 0) & (mdisk+mbulge > 0) & (typeg == 0))
    sam_ratio_halo_gal[index,:]    = bin_it_halo(x=np.log10(mvir_s[ind]) - np.log10(float(h0)),
                                                 y=np.log10(sam_stars[ind]/sam_subhalo[ind]))
    ind = np.where((specific_angular_momentum_disk_star > 0) & (mdisk+mbulge > 0) & (typeg == 0))
    sam_ratio_halo_disk[index,:]   = bin_it_halo(x=np.log10(mvir_s[ind]) - np.log10(float(h0)),
                                                 y=np.log10(specific_angular_momentum_disk_star[ind]/sam_subhalo[ind]))

    ind = np.where((specific_angular_momentum_disk_gas > 0) & (mdisk+mbulge > 0) & (typeg == 0))
    sam_ratio_halo_disk_gas[index,:]   = bin_it_halo(x=np.log10(mvir_s[ind]) - np.log10(float(h0)),
                                                     y=np.log10(specific_angular_momentum_disk_gas[ind]/sam_subhalo[ind]))
  
    ind = np.where((specific_angular_momentum_disk_gas_atom > 0) & (mdisk+mbulge > 0) & (mbulge/(mdisk+mbulge) < 0.5) & (typeg == 0))
    sam_gas_disk_atom[index,:]= bin_it(x=np.log10(mdisk[ind]+mbulge[ind]) - np.log10(float(h0)),
                                       y=np.log10(specific_angular_momentum_disk_gas_atom[ind]) - np.log10(float(h0)))
    
    ind = np.where((specific_angular_momentum_disk_gas_mol > 0) & (mdisk+mbulge > 0) & (mbulge/(mdisk+mbulge) < 0.5) & (typeg == 0))
    sam_gas_disk_mol[index,:]= bin_it(x=np.log10(mdisk[ind]+mbulge[ind]) - np.log10(float(h0)),
                                      y=np.log10(specific_angular_momentum_disk_gas_mol[ind]) - np.log10(float(h0)))
    
    ind = np.where((sam_subhalo > 0) & (mdisk+mbulge > 0) & (mbulge/(mdisk+mbulge) < 0.5) & (typeg == 0))
    sam_halo[index,:]       = bin_it(x=np.log10(mdisk[ind]+mbulge[ind]) - np.log10(float(h0)), 
			             y=np.log10(sam_subhalo[ind]) - np.log10(float(h0)))

    return (lh, ls, bt, ms)

def plot_specific_am(plt, outdir, obsdir, sam_stars_disk, sam_gas_disk_atom, sam_gas_disk_mol, sam_halo):

    fig = plt.figure(figsize=(9.5,9.5))
    xtit = "$\\rm log_{10} (\\rm M_{\\star}/M_{\odot})$"
    ytit = "$\\rm log_{10} (\\rm j_{\\rm disk}/kpc\\, km s^{-1})$"
    xmin, xmax, ymin, ymax = 8, 11.5, 1.5, 5
    xleg = xmax - 0.2 * (xmax - xmin)
    yleg = ymax - 0.1 * (ymax - ymin)

    subplots = (221, 222, 223, 224)
    indz = (0, 1, 2, 3)
    zinplot = (0, 0.5, 1, 2) 

    # LTG ##################################
    for z,s,p in zip(zinplot, indz, subplots):
	    ax = fig.add_subplot(p)
	    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))
            ax.text(xleg, yleg, 'z=%s' % str(z))

	    ind = np.where(sam_halo[s,0,:] != 0)
	    xplot = xmf[ind]
	    yplot = sam_halo[s,0,ind] + 3.0
	    errdn = sam_halo[s,1,ind]
	    errup = sam_halo[s,2,ind]
	    ax.plot(xplot,yplot[0],color='k',label="DM")
	    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='k', alpha=0.2,interpolate=True)
	    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='k', alpha=0.2,interpolate=True)

            #Predicted sAM-mass for disks in disk=dominated galaxies
            ind = np.where(sam_stars_disk[s,0,:] != 0)
            xplot = xmf[ind]
            yplot = sam_stars_disk[s,0,ind]+ 3.0
            errdn = sam_stars_disk[s,1,ind]
            errup = sam_stars_disk[s,2,ind]
            ax.plot(xplot,yplot[0],color='r',label="stars")
            ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='r', alpha=0.5,interpolate=True)
            ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='r', alpha=0.5,interpolate=True)

            #Predicted size-mass for disks in disk=dominated galaxies
            ind = np.where(sam_gas_disk_atom[s,0,:] != 0)
            xplot = xmf[ind]
            yplot = sam_gas_disk_atom[s,0,ind] + 3.0
            errdn = sam_gas_disk_atom[s,1,ind]
            errup = sam_gas_disk_atom[s,2,ind]
            ax.plot(xplot,yplot[0],color='b',label="atomic ISM")
            ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='b', alpha=0.5,interpolate=True)
            ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='b', alpha=0.5,interpolate=True)
    
            #Predicted size-mass for disks in disk=dominated galaxies
            ind = np.where(sam_gas_disk_mol[s,0,:] != 0)
            xplot = xmf[ind]
            yplot = sam_gas_disk_mol[s,0,ind] + 3.0
            errdn = sam_gas_disk_mol[s,1,ind]
            errup = sam_gas_disk_mol[s,2,ind]
            ax.plot(xplot,yplot[0],color='g',label="molecular ISM")
            ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='g', alpha=0.5,interpolate=True)
            ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='g', alpha=0.5,interpolate=True)

	    common.prepare_legend(ax, ['k'], loc=2)


    common.savefig(outdir, fig, 'specific_am.pdf')
  
    #plot angular momentum components separately. 
    fig = plt.figure(figsize=(12,5))
    s = 0 
    #plot stars
    xtit = "$\\rm log_{10} (\\rm M_{\\star}/M_{\odot})$"
    ytit = "$\\rm log_{10} (\\rm j_{\\star, disk}/kpc\\, km s^{-1})$"
    xmin, xmax, ymin, ymax = 8, 11.5, 1.5, 4
    xleg = xmax - 0.2 * (xmax - xmin)
    yleg = ymax - 0.1 * (ymax - ymin)

    ax = fig.add_subplot(131)
    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))

    jst, jmole, jatomic = common.load_observation('/mnt/su3ctm/clagos/SHArk_static/ObsAndModelData/Models/SharkVariations/', 'AngularMomentum.dat', [0,1,2])
    jsL18    = np.zeros(shape = (3, len(xmf)))
    jmolL18  = np.zeros(shape = (3, len(xmf)))
    jatomL18 = np.zeros(shape = (3, len(xmf)))
    i = 0
    p =0
    for j in range(0,len(jst)):
	jsL18[i,p]    = jst[j]
        jmolL18[i,p]  = jmole[j]
        jatomL18[i,p] = jatomic[j]
        p = p + 1
        if(p >= len(xmf)):
		p = 0
		i = i +1
   
    #Predicted sAM-mass for disks in disk=dominated galaxies
    ind = np.where(sam_stars_disk[s,0,:] != 0)
    xplot = xmf[ind]
    yplot = sam_stars_disk[s,0,ind]+ 3.0
    errdn = sam_stars_disk[s,1,ind]
    errup = sam_stars_disk[s,2,ind]
    ax.plot(xplot,yplot[0],color='r')
    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='r', alpha=0.5,interpolate=True)
    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='r', alpha=0.5,interpolate=True)

    ind = np.where(jsL18[0,:] != 0)
    xplot = xmf[ind]
    yplot = jsL18[0,ind]+ 3.0
    errdn = jsL18[1,ind]
    errup = jsL18[2,ind]
    ax.plot(xplot,yplot[0],color='r',linestyle='dashed')
    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='r', linestyle='dashed', alpha=0.3,interpolate=True)
    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='r', linestyle='dashed', alpha=0.3,interpolate=True)

    ms, js = common.load_observation(obsdir, 'SizesAndAM/Posti18.dat', [0,1])
    ax.plot(ms, js, 'r+',fillstyle='none', label="Posti+18")

    bt, msO14, mgO14, jsO14, jgO14, jmolO14 = common.load_observation(obsdir, 'SizesAndAM/Obreschkow14_FP.dat', [2,7,8,12,14,15])
    ax.plot(msO14, jsO14, 'ro',fillstyle='none', label="Obreschkow+14")

    mg, msB17, jgB17, jsB17 = common.load_observation(obsdir, 'SizesAndAM/LITTLETHINGS_Butler16.dat', [1,3,7,9])
    ax.plot(msB17, jsB17, 'rs',fillstyle='none',label="Butler+16 (indiv)")

    common.prepare_legend(ax, ['r', 'r', 'r'], loc=2)

    #plot molecular gas
    xtit = "$\\rm log_{10} (\\rm M_{\\star}/M_{\odot})$"
    ytit = "$\\rm log_{10} (\\rm j_{\\rm H_2}/kpc\\, km s^{-1})$"
    ax = fig.add_subplot(132)
    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))

    #Predicted size-mass for disks in disk=dominated galaxies
    ind = np.where(sam_gas_disk_mol[s,0,:] != 0)
    xplot = xmf[ind]
    yplot = sam_gas_disk_mol[s,0,ind] + 3.0
    errdn = sam_gas_disk_mol[s,1,ind]
    errup = sam_gas_disk_mol[s,2,ind]
    ax.plot(xplot,yplot[0],color='g', label="ISM/stars AM transfer")
    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='g', alpha=0.5,interpolate=True)
    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='g', alpha=0.5,interpolate=True)

    ind = np.where(jmolL18[0,:] != 0)
    xplot = xmf[ind]
    yplot = jmolL18[0,ind]+ 3.0
    errdn = jmolL18[1,ind]
    errup = jmolL18[2,ind]
    ax.plot(xplot,yplot[0],color='g',linestyle='dashed', label="Lagos+18")
    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='g', linestyle='dashed', alpha=0.3,interpolate=True)
    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='g', linestyle='dashed', alpha=0.3,interpolate=True)

    ax.plot(msO14, jmolO14, 'go',fillstyle='none')
    common.prepare_legend(ax, ['k'], loc=2)

    #plot atomic gas
    xtit = "$\\rm log_{10} (\\rm M_{\\star}/M_{\odot})$"
    ytit = "$\\rm log_{10} (\\rm j_{\\rm HI}/kpc\\, km s^{-1})$"
    ax = fig.add_subplot(133)
    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))

    #Predicted size-mass for disks in disk=dominated galaxies
    ind = np.where(sam_gas_disk_atom[s,0,:] != 0)
    xplot = xmf[ind]
    yplot = sam_gas_disk_atom[s,0,ind] + 3.0
    errdn = sam_gas_disk_atom[s,1,ind]
    errup = sam_gas_disk_atom[s,2,ind]
    ax.plot(xplot,yplot[0],color='b')
    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='b', alpha=0.5,interpolate=True)
    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='b', alpha=0.5,interpolate=True)

    ind = np.where(jatomL18[0,:] != 0)
    xplot = xmf[ind]
    yplot = jatomL18[0,ind]+ 3.0
    errdn = jatomL18[1,ind]
    errup = jatomL18[2,ind]
    ax.plot(xplot,yplot[0],color='b',linestyle='dashed')
    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='b', linestyle='dashed', alpha=0.3,interpolate=True)
    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='b', linestyle='dashed', alpha=0.3,interpolate=True)

    ax.plot(msB17, jgB17, 'bs',fillstyle='none')
    ax.plot(msO14, jgO14, 'bo',fillstyle='none')

    common.prepare_legend(ax, ['k'], loc=2)

    common.savefig(outdir, fig, 'specific_am_z0_components.pdf')

    #for i in range (0,3):
    #	    for x,y,z in zip(sam_stars_disk[s,i,:],sam_gas_disk_mol[s,i,:],sam_gas_disk_atom[s,i,:]):
    #           print x,y,z

def plot_specific_am_ratio(plt, outdir, obsdir, sam_ratio_halo_disk, sam_ratio_halo_gal, sam_ratio_halo_disk_gas):

    fig = plt.figure(figsize=(9.5,9.5))
    xtit = "$\\rm log_{10} (\\rm M_{\\rm halo}/M_{\odot})$"
    ytit = "$\\rm log_{10} (\\rm j_{\\star}/j_{\\rm halo}$)"
    xmin, xmax, ymin, ymax = 10, 15, -3, 1
    xleg = xmax - 0.2 * (xmax - xmin)
    yleg = ymax - 0.1 * (ymax - ymin)

    subplots = (221, 222, 223, 224)
    indz = (0, 1, 2, 3)
    zinplot = (0, 0.5, 1, 2) 

    # LTG ##################################
    for z,s,p in zip(zinplot, indz, subplots):
	    ax = fig.add_subplot(p)
	    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))
            ax.text(xleg, yleg, 'z=%s' % str(z))

	    ind = np.where(sam_ratio_halo_gal[s,0,:] != 0)
	    xplot = xmfh[ind]
	    yplot = sam_ratio_halo_gal[s,0,ind]
	    errdn = sam_ratio_halo_gal[s,1,ind]
	    errup = sam_ratio_halo_gal[s,2,ind]
	    ax.plot(xplot,yplot[0],color='k',label="all stars")
	    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='k', alpha=0.2,interpolate=True)
	    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='k', alpha=0.2,interpolate=True)

	    ind = np.where(sam_ratio_halo_disk[s,0,:] != 0)
	    xplot = xmfh[ind]
	    yplot = sam_ratio_halo_disk[s,0,ind]
	    errdn = sam_ratio_halo_disk[s,1,ind]
	    errup = sam_ratio_halo_disk[s,2,ind]
	    ax.plot(xplot,yplot[0],color='g',label="disk stars")
	    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='g', alpha=0.2,interpolate=True)
	    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='g', alpha=0.2,interpolate=True)

	    ind = np.where(sam_ratio_halo_disk_gas[s,0,:] != 0)
	    xplot = xmfh[ind]
	    yplot = sam_ratio_halo_disk_gas[s,0,ind]
	    errdn = sam_ratio_halo_disk_gas[s,1,ind]
	    errup = sam_ratio_halo_disk_gas[s,2,ind]
	    ax.plot(xplot,yplot[0],color='b',label="disk gas")
	    ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='b', alpha=0.2,interpolate=True)
	    ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='b', alpha=0.2,interpolate=True)

	    common.prepare_legend(ax, ['k'], loc=2)


    common.savefig(outdir, fig, 'specific_am_ratio.pdf')
  
def plot_lambda(plt, outdir, obsdir, lambdaH, lambda_disk, bt, ms):

    fig = plt.figure(figsize=(5,9))
    xtit = "$\\rm log_{10}(\\lambda_{\\rm halo})$"
    ytit = "$\\rm log_{10}(\\lambda_{\\rm disk})$"
    xmin, xmax, ymin, ymax = -3, 0, -1.5, 0.8
    xleg = xmax - 0.3 * (xmax - xmin)
    yleg = ymax - 0.1 * (ymax - ymin)

    med = np.zeros(shape = (3, len(xlf)))

    ax = fig.add_subplot(211)
    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))
    ax.text(xleg, yleg, 'all galaxies')

    ind = np.where((lambdaH > 0) & (lambda_disk > 0) & (lambda_disk < 10) & (ms > 9))
    xdata = np.log10(lambdaH[ind])
    ydata = np.log10(lambda_disk[ind])
    us.density_contour(ax, xdata, ydata, 30, 30) #, **contour_kwargs)

    coeff = np.corrcoef(np.log10(lambdaH[ind]),np.log10(lambda_disk[ind]))
    ax.text(xleg, ymax - 0.2 * (ymax - ymin), 'R=%s' % str(np.around(coeff[0,1], decimals=3)))

    med[:] = us.wmedians(x=np.log10(lambdaH[ind]), y=np.log10(lambda_disk[ind]), xbins = xlf, low_numbers=True)
    ind    = np.where(med[0,:] != 0)
    xobs   = xlf[ind]
    yobs   = med[0,ind]
    yerrdn = med[1,ind]
    yerrup = med[2,ind]
    ax.errorbar(xobs, yobs[0], yerr=[yerrdn[0],yerrup[0]], ls='None', mfc='None', ecolor = 'grey', mec='grey',linestyle='solid', color='k')
 
    ax = fig.add_subplot(212)
    xmin, xmax, ymin, ymax = -3, 0, -1.3, 0.3
    xleg = xmax - 0.3 * (xmax - xmin)
    yleg = ymax - 0.1 * (ymax - ymin)
    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1, 1))
    ax.text(xleg, yleg, 'disk-dominated')

    ind = np.where((lambdaH > 0) & (lambda_disk > 0) & (bt < 0.5) & (ms > 9))
    xdata = np.log10(lambdaH[ind])
    ydata = np.log10(lambda_disk[ind])
    us.density_contour(ax, xdata, ydata, 30, 30) #, **contour_kwargs)
    coeff = np.corrcoef(np.log10(lambdaH[ind]),np.log10(lambda_disk[ind]))
    ax.text(xleg, ymax - 0.2 * (ymax - ymin), 'R=%s' % str(np.around(coeff[0,1], decimals=3)))

    med[:] = us.wmedians(x=np.log10(lambdaH[ind]), y=np.log10(lambda_disk[ind]), xbins = xlf, low_numbers=True)
    ind    = np.where(med[0,:] != 0)
    xobs   = xlf[ind]
    yobs   = med[0,ind]
    yerrdn = med[1,ind]
    yerrup = med[2,ind]
    ax.errorbar(xobs, yobs[0], yerr=[yerrdn[0],yerrup[0]], ls='None', mfc='None', ecolor = 'grey', mec='grey',linestyle='solid', color='k')

    common.savefig(outdir, fig, 'lambda_relation.pdf')


def main(modeldir, outdir, subvols, obsdir):

    plt = common.load_matplotlib()
    fields = {'galaxies': ('mstars_disk', 'mstars_bulge', 'mstars_burst_mergers', 'mstars_burst_diskinstabilities',
                           'mstars_bulge_mergers_assembly', 'mstars_bulge_diskins_assembly', 'm_bh', 'rstar_disk', 'rstar_bulge', 'type', 
                           'specific_angular_momentum_disk_star', 'specific_angular_momentum_bulge_star',
                           'specific_angular_momentum_disk_gas', 'specific_angular_momentum_bulge_gas',
                           'specific_angular_momentum_disk_gas_atom', 'specific_angular_momentum_disk_gas_mol',
                           'lambda_subhalo', 'mvir_subhalo', 'mvir_hosthalo', 'matom_disk', 'mmol_disk', 'mgas_disk',
                           'matom_bulge', 'mmol_bulge', 'mgas_bulge')}

    # Loop over redshift and subvolumes
    sam_stars_disk    = np.zeros(shape = (len(zlist), 3, len(xmf)))
    sam_gas_disk_atom = np.zeros(shape = (len(zlist), 3, len(xmf)))
    sam_gas_disk_mol  = np.zeros(shape = (len(zlist), 3, len(xmf)))
     
    sam_halo             = np.zeros(shape = (len(zlist), 3, len(xmf)))
    sam_ratio_halo_disk  = np.zeros(shape = (len(zlist), 3, len(xmfh)))
    sam_ratio_halo_gal   = np.zeros(shape = (len(zlist), 3, len(xmfh)))
    sam_ratio_halo_disk_gas = np.zeros(shape = (len(zlist), 3, len(xmfh)))

    for index in range(0,4):
        hdf5_data = common.read_data(modeldir, zlist[index], fields, subvols)
        (lh, ls, bt, ms)  = prepare_data(hdf5_data, index, sam_stars_disk, sam_gas_disk_atom, sam_gas_disk_mol, sam_halo, sam_ratio_halo_disk, 
                     sam_ratio_halo_gal, sam_ratio_halo_disk_gas)
        if(index  == 0):
		lambdaH = lh
		lambda_disk = ls
                BT_ratio = bt
	        stellar_mass = ms

    plot_specific_am(plt, outdir, obsdir, sam_stars_disk, sam_gas_disk_atom, sam_gas_disk_mol, sam_halo)
    plot_specific_am_ratio(plt, outdir, obsdir, sam_ratio_halo_disk, sam_ratio_halo_gal, sam_ratio_halo_disk_gas)
    plot_lambda(plt, outdir, obsdir, lambdaH, lambda_disk, BT_ratio, stellar_mass)

if __name__ == '__main__':
    main(*common.parse_args(requires_snapshot=False))
