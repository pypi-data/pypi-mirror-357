import sys
import numpy as np
import matplotlib.pyplot as plt
import inso.astro as astro
import inso.inso as inso
import inso.minmax as minmax

deg_to_rad = np.pi/180.

#=========================================================================================
def display(figureId = None):

    list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]

    figureId = str(figureId)

    if figureId is None or figureId not in list:
        print('')
        print('This code generates the figures of the paper "On the computation of several « insolation » quantities')
        print('relevant to climatology or planetology" (Didier Paillard, 2025)')
        print('')
        print('List of available figures: ', list)
        print('')
        return

    ########################################
    if figureId == "1":
        a = astro.AstroLaskar2004()     # initialisation un peu lente
        t = np.linspace(-100,0,101)
        obliquity = a.obliquity(t)
        eccentricity = a.eccentricity(t)
        climatic_precession = a.precession_angle(t)
        lat = 65*deg_to_rad
        pos = 180*deg_to_rad
        plt.plot(t,1365*inso.inso_dayly_radians(pos,lat,obliquity,eccentricity,climatic_precession))
        plt.plot(t,1365*inso.inso_dayly_time_radians(pos,lat,obliquity,eccentricity,climatic_precession))
        plt.title("daily insolation 65°N, september '21st'")
        plt.ylabel("inso (W/m2)")
        plt.xlabel("time (kyr)")
        plt.show()
    
    ########################################
    elif figureId == "2":
        a = astro.AstroLaskar2004()
        t = np.linspace(-500,0,501)
        obliquity = a.obliquity(t)
        eccentricity = a.eccentricity(t)
        climatic_precession = a.precession_angle(t)
        solar = 1365
    
        gg = np.empty(len(t))
        for i in range(len(t)):
            gg[i] = solar*inso.inso_mean_radians(0,np.pi,65*deg_to_rad,obliquity[i],eccentricity[i],climatic_precession[i])
        plt.plot(t,gg)
        for i in range(len(t)):
            gg[i] = solar*inso.inso_caloric_summer_NH(65*deg_to_rad,obliquity[i],eccentricity[i],climatic_precession[i])
        plt.plot(t,gg)
        plt.title("integrated summer inso")
        plt.ylabel("inso (W/m2)")
        plt.xlabel("time (kyr)")
        plt.show()
    
    ########################################
    elif figureId == "3": # mid-points vs averaged daily insolation, on a low-resolution grid
        obliquity = 23.439291111111835*deg_to_rad
        eccentricity = 0.01670236225492288
        climatic_precession = 102.91794451250462*deg_to_rad
        fig, axs = plt.subplots(1,3,figsize=(15, 4))
        lat = np.linspace(-85,85,18)
        g = np.empty(len(lat))
        for i in range(len(lat)):
            g[i] = 1365*inso.inso_dayly_radians(90*deg_to_rad,lat[i]*deg_to_rad,obliquity,eccentricity,climatic_precession)
        axs[0].scatter(lat,g)
        for i in range(len(lat)):
            g[i] = 1365*inso.inso_mean_lat_radians(90*deg_to_rad,(lat[i]-5)*deg_to_rad,(lat[i]+5)*deg_to_rad,obliquity,eccentricity,climatic_precession)
        axs[0].scatter(lat,g)
        axs[0].set_title('daily inso, mid-point or mean')
        axs[0].set_xlabel('latitude')
        axs[0].set_ylabel('inso (W.m-2)')
        for i in range(len(lat)):
            mid = 1365*inso.inso_dayly_radians(90*deg_to_rad,lat[i]*deg_to_rad,obliquity,eccentricity,climatic_precession)
            mean = 1365*inso.inso_mean_lat_radians(90*deg_to_rad,(lat[i]-5)*deg_to_rad,(lat[i]+5)*deg_to_rad,obliquity,eccentricity,climatic_precession)
            g[i] = mid-mean
        axs[1].scatter(lat,g)
        axs[1].set_title('difference (mean - mid-point)')
        axs[1].set_xlabel('latitude')
        axs[1].set_ylabel('inso (W.m-2)')
        #plt.show()
        for i in range(len(lat)):
            mid = 1365*inso.inso_dayly_radians(90*deg_to_rad,lat[i]*deg_to_rad,obliquity,eccentricity,climatic_precession)
            mean = 1365*inso.inso_mean_lat_radians(90*deg_to_rad,(lat[i]-5)*deg_to_rad,(lat[i]+5)*deg_to_rad,obliquity,eccentricity,climatic_precession)
            if mean == 0:
                g[i] = 0
            else:
                g[i] = 100*abs((mid-mean)/mean)
        axs[2].scatter(lat,g)
        axs[2].set_title('relative difference')
        axs[2].set_xlabel('latitude')
        axs[2].set_ylabel('percent difference (%)')
        plt.show()
    
    ########################################
    elif figureId == "4":
        fig, axs = plt.subplots(2,2,figsize=(14, 10))
        solar = 1365
        obliquity = 23.4*deg_to_rad
        ecc = 0.016
        pre = 102*deg_to_rad
        plt.sca(axs[0][0])
        minmax.plot_inso_with_min_max(solar,ecc,obliquity,pre)
        plt.title(r'Earth insolation today (W/m2) - $\epsilon = 23.4° ; e = 0.016 ; \varpi = 102°$')
        obliquity = 23.4*deg_to_rad
        ecc = 0.5
        pre = 102*deg_to_rad
        plt.sca(axs[1][0])
        minmax.plot_inso_with_min_max(100,ecc,obliquity,pre)
        plt.title(r'insolation (%) - $\epsilon = 23.4° ; e = 0.5 ; \varpi = 102°$')
        obliquity = 60*deg_to_rad
        ecc = 0.5
        pre = 12*deg_to_rad
        plt.sca(axs[1][1])
        minmax.plot_inso_with_min_max(100,ecc,obliquity,pre)
        plt.title(r'insolation (%) - $\epsilon = 60° ; e = 0.5 ; \varpi = 12°$')
        a = astro.AstroLaskarMars2004()
        t = -10
        e_mars = a.eccentricity(t)
        eps_mars = a.obliquity(t)
        p_mars = a.precession_angle(t)
        mars_a = 1.523679335          # semi-major axis in A.U.
        solarC = 1365/(mars_a*mars_a)
        plt.sca(axs[0][1])
        minmax.plot_inso_with_min_max(solarC,e_mars,eps_mars,p_mars)
        plt.title(r'Mars insolation at 10 kyrBP (W/m2)- $\epsilon$ = ' + f"{eps_mars/deg_to_rad:.1f}"\
                  + r'° ; $e$ = ' + f"{e_mars:.1f}" + r' ; $\varpi$ = ' + f"{p_mars/deg_to_rad:.1f}" + '°')
        plt.show()
    
    ########################################
    elif figureId == "5":
        def add_Earth_Mars():
            #Earth - today
            plt.gca().plot([np.cos(23.4*deg_to_rad)], [0.016], '*',color='b')
            #Earth - range (min & max over the last 100 Myr, Laskar2004)
            max_e = 0.06695670152051249
            min_e = 0.00014
            cos_max_eps = 0.9100755285619001
            cos_min_eps = 0.927617189895506
            plt.gca().add_patch(plt.Rectangle( (cos_max_eps,min_e), cos_min_eps-cos_max_eps, max_e-min_e, ls=":", lw=1, ec="b", fc="none" ))
            #Mars - today
            plt.gca().plot([np.cos(25.2*deg_to_rad)], [0.093], '*',color='r')
            #Mars - range (min & max over the last 20 Myr, Laskar2004)
            max_e = 0.12309977543738711
            min_e = 0.0011399355994509593
            cos_max_eps = 0.6734529793159241
            cos_min_eps = 0.9673561983722324
            plt.gca().add_patch(plt.Rectangle( (cos_max_eps,min_e), cos_min_eps-cos_max_eps, max_e-min_e, ls=":", lw=1, ec="r", fc="none" ))
        fig, axs = plt.subplots(1,2,figsize=(12, 5))
        plt.sca(axs[0])
        minmax.plot_Ldomains()
        add_Earth_Mars()
        plt.sca(axs[1])
        minmax.plot_Hdomains()
        add_Earth_Mars()
        plt.show()
    
    ########################################
    elif figureId == "6":
        a = astro.AstroLaskar2004()
        t = np.linspace(-500,0,501)
        obliquity = a.obliquity(t)
        eccentricity = a.eccentricity(t)
        climatic_precession = a.precession_angle(t)
        solar = 1365
        
        gg = np.empty(len(t))
        for i in range(len(t)):
            gg[i] = solar*minmax.largest_max(0*deg_to_rad,eccentricity[i],obliquity[i],climatic_precession[i])[1]
        plt.plot(t,gg)
        for i in range(len(t)):
            gg[i] = solar*minmax.smallest_min(0*deg_to_rad,eccentricity[i],obliquity[i],climatic_precession[i])[1]
        plt.plot(t,gg)
        plt.title("max/min inso at the equator")
        plt.ylabel("inso (W/m2)")
        plt.xlabel("time (kyr)")
        plt.show()
    
    ########################################
    elif figureId == "7":
        a = astro.AstroLaskar2004()
        t = np.linspace(-500,0,501)
        obliquity = a.obliquity(t)
        eccentricity = a.eccentricity(t)
        climatic_precession = a.precession_angle(t)
        solar = 1365
        
        fig, axs = plt.subplots(1,2,figsize=(12, 4))
        gg = np.empty(len(t))
        for i in range(len(t)):
            gg[i] = solar*minmax.largest_max(10*deg_to_rad,eccentricity[i],obliquity[i],climatic_precession[i])[1]
        axs[0].plot(t,gg)
        axs[0].set_title("maximum inso at 10°N")
        axs[0].set_ylabel("inso (W/m2)")
        axs[0].set_xlabel("time (kyr)")
        for i in range(len(t)):
            gg[i] = solar*minmax.largest_max(15*deg_to_rad,eccentricity[i],obliquity[i],climatic_precession[i])[1]
        axs[1].plot(t,gg)
        axs[1].set_title("maximum inso at 15°N")
        axs[1].set_ylabel("inso (W/m2)")
        axs[1].set_xlabel("time (kyr)")
        plt.show()
    
    ########################################
    elif figureId == "8":
        a = astro.AstroLaskar2004()
        t = np.linspace(-500,0,501)
        obliquity = a.obliquity(t)
        eccentricity = a.eccentricity(t)
        climatic_precession = a.precession_angle(t)
        solar = 1365
        
        fig, axs = plt.subplots(1,2,figsize=(12, 4))
        gg = np.empty(len(t))
        for i in range(len(t)):
            gg[i] = minmax.largest_max(65*deg_to_rad,eccentricity[i],obliquity[i],climatic_precession[i])[0]/deg_to_rad
        axs[0].plot(t,gg)
        axs[0].set_title("date (true longitude in °) of the maximum inso at 65°N")
        axs[0].set_ylabel("true longitude (°)")
        axs[0].set_xlabel("time (kyr)")
        for i in range(len(t)):
            gg[i] = solar*(minmax.largest_max(65*deg_to_rad,eccentricity[i],obliquity[i],climatic_precession[i])[1] \
                -inso.inso_dayly_radians(90*deg_to_rad,65*deg_to_rad,obliquity[i],eccentricity[i],climatic_precession[i]))
        axs[1].plot(t,gg)
        axs[1].set_title("difference between maximum inso and inso at the solstice")
        axs[1].set_ylabel("∆inso (W/m2)")
        axs[1].set_xlabel("time (kyr)")
        plt.show()
    
    ########################################
    elif figureId == "9":
        solar = 1365.
        lat = 65*deg_to_rad
        T = 3600*24*365.2425   # 1 year in seconds
    
        a = astro.AstroLaskar2004()
        t = np.linspace(-500,-0,501)
    
        t5 = np.empty(len(t))
        for i in range(len(t)):
            t5[i] = solar*inso.inso_mean_radians(0,2*np.pi,lat,a.obliquity(t[i]),a.eccentricity(t[i]),a.precession_angle(t[i]))
        m5 = np.mean(t5)
        s5 = np.std(t5)
    
        t2 = np.empty(len(t))
        thresh = 350/solar
        for i in range(len(t)):
            t2[i] = 1e-9*solar*T*minmax.integrated_inso_above(thresh,lat,a.eccentricity(t[i]),a.obliquity(t[i]),a.precession_angle(t[i]))
        m2 = np.mean(t2)
        s2 = np.std(t2)
        
        t3 = np.empty(len(t))
        thresh = 300/solar
        for i in range(len(t)):
            t3[i] = 1e-9*solar*T*minmax.integrated_inso_above(thresh,lat,a.eccentricity(t[i]),a.obliquity(t[i]),a.precession_angle(t[i]))
        m3 = np.mean(t3)
        s3 = np.std(t3)
    
        t4 = np.empty(len(t))
        thresh = 400/solar
        for i in range(len(t)):
            t4[i] = 1e-9*solar*T*minmax.integrated_inso_above(thresh,lat,a.eccentricity(t[i]),a.obliquity(t[i]),a.precession_angle(t[i]))
        m4 = np.mean(t4)
        s4 = np.std(t4)
    
        t0 = np.empty(len(t))
        for i in range(len(t)):
            t0[i] = solar*inso.inso_caloric_summer_NH(lat,a.obliquity(t[i]),a.eccentricity(t[i]),a.precession_angle(t[i]))
        m0 = np.mean(t0)
        s0 = np.std(t0)
    
        t1 = np.empty(len(t))
        for i in range(len(t)):
            t1[i] = solar*inso.inso_dayly_radians(np.pi/2,lat,a.obliquity(t[i]),a.eccentricity(t[i]),a.precession_angle(t[i]))
        m1 = np.mean(t1)
        s1 = np.std(t1)
    
        fig, ax = plt.subplots()
        stp = 3
        y0 = -12
        ax.plot(t,y0+(t1-m1)/s1,label='daily')
        y0 += stp
        ax.plot(t,y0+(t4-m4)/s4,label='>400')
        y0 += stp
        ax.plot(t,y0+(t0-m0)/s0,label='caloric')
        ax.plot(t,y0+(t2-m2)/s2,":",label='>350')
        y0 += stp
        ax.plot(t,y0+(t3-m3)/s3,label='>300')
        y0 += stp
        ax.plot(t,y0+(t5-m5)/s5,label='annual')
        ax.get_yaxis().set_visible(False)
        plt.xlabel('time (kyr)')
        plt.legend(loc='upper center', bbox_to_anchor=(.5, 1.08),ncol=3)
        plt.show()
    
    ########################################
    elif figureId == "A1":
        fig, axs = plt.subplots(1,2,figsize=(12, 4))
        minmax.subplot_boundaries(axs[0],.2)
        minmax.subplot_boundaries(axs[1],.5)
        plt.show()
    
    ########################################
    elif figureId == "A2":
        for c in (0.05, 0.25, 0.5, 0.7, 0.9, 0.99):
            x = np.linspace(0,1,100)
            y = np.empty(len(x))
            for i in range(len(x)):
                y[i] = minmax.solHofU(c,x[i])
            plt.plot(x,y,label='c = '+str(c))
            x = np.linspace(minmax.h0(c)+1e-5,np.pi-1e-5,100)
            y = np.empty(len(x))
            for i in range(len(x)):
                y[i] = minmax.solUofH(c,x[i])
            plt.plot(y,x,color=plt.gca().lines[-1].get_color())
        plt.title(r'implicit solutions for the critical points')
        plt.xlabel(r'u = $cos^{2}(\lambda)$')
        plt.ylabel(r'$h$')
        plt.legend()
        plt.show()
    
    ########################################
    elif figureId == "A3":          # solHofU(c,h)  +  e2L(c,u)
        fig, axs = plt.subplots(1,2,figsize=(12, 4))
        plt.sca(axs[0])
        for c in (0, 0.1, 0.3, 0.5, 0.7, 0.9, 1):         # plots some of the solHofU curves
            minmax.my_plot(lambda z: minmax.solHofU(c,z),0,1,label='c = '+str(c))
        plt.title(r'$h_{SOL}(c,u)$')
        plt.xlabel(r'u = $cos^{2}(\lambda)$')
        plt.ylabel(r'$h_{SOL}(c,u)$')
        plt.legend()
        plt.sca(axs[1])
        #--------
        if False:
            for c in (0.05, 0.25, 0.5, 0.7, 0.9, 0.99):         # plots some of the e2L curves functions of u
                minmax.my_plot(lambda z: np.sqrt(minmax.e2L(c,z)),0,1,label='c = '+str(c))
                plt.title(r'eccentricity '+'$e_{L}(c,u)$')
                plt.xlabel(r'u = $cos^{2}(\lambda)$')
                plt.ylabel(r'$e_{L}(c,u)$')
        #--------
        for c in (0, 0.1, 0.3, 0.5, 0.7, 0.9, 1):               # plots some of the e2L curves functions of lambda
            minmax.my_plot(lambda z: np.sqrt(minmax.e2L(c,np.square(np.cos(z)))),0,np.pi/2,label='c = '+str(c))
        plt.title(r'eccentricity '+'$e_{L}(c,cos^{2}(\lambda))$')
        plt.xlabel(r'true longitude $\lambda$')
        plt.ylabel(r'$e_{L}(c,cos^{2}(\lambda))$')
        plt.legend()
        plt.show()
    
    ########################################
    elif figureId == "A4":
        minmax.plot_Ldomains()
        plt.plot([.38], [0.3], '*',color='r')
        plt.plot([.5], [0.5], '*',color='r')
        plt.plot([.9], [0.5], '*',color='r')
        plt.plot([.37], [0.3], '*',color='r')
        plt.plot([.9], [0.05], '*',color='r')
        plt.plot([.9], [0.3], '*',color='r')
        plt.show()
    
    ########################################
    elif figureId == "A5":
        fig, axs = plt.subplots(2,3,figsize=(16, 10))
        minmax.subplot_lbd_minmaxL(axs[0][0],.3,np.arccos(.38))
        minmax.subplot_lbd_minmaxL(axs[0][1],.5,np.arccos(.5))
        minmax.subplot_lbd_minmaxL(axs[0][2],.5,np.arccos(.9))
        minmax.subplot_lbd_minmaxL(axs[1][0],.3,np.arccos(.37))
        minmax.subplot_lbd_minmaxL(axs[1][1],.05,np.arccos(.9))
        minmax.subplot_lbd_minmaxL(axs[1][2],.3,np.arccos(.9))
        plt.show()
    
    ########################################
    elif figureId == "A6":          # plot h0(c)
        minmax.my_plot(minmax.h0,0,1,n=100,label='',color="")
        plt.title(r'$h_{0}(c)$')
        plt.xlabel(r'c = cos($\epsilon$)')
        plt.ylabel(r'$h_{0}(c)$')
        plt.show()
    
    ########################################
    elif figureId == "A7":          # e2H(c,h)
        fig, axs = plt.subplots(2,2,figsize=(12, 10))
        plt.sca(axs[0][0])
        for c in (0.6, 0.7, 0.8, 0.9, 0.95, 0.99):         # plots some of the solUofH curves
            minmax.my_plot(lambda z: minmax.solUofH(c,z),minmax.h0(c)+1e-5,np.pi,label='c = '+str(c))
        plt.title(r'$u_{SOL}(c,h)$')
        plt.xlabel(r'$h$')
        plt.ylabel(r'$u_{SOL}(c,h)$')
        plt.legend()
        plt.sca(axs[0][1])
        for c in (0.6, 0.5, 0.4, 0.3, 0.2, 0.1):         # plots some of the solUofH curves
            minmax.my_plot(lambda z: minmax.solUofH(c,z),minmax.h0(c)+1e-5,np.pi,label='c = '+str(c))
        plt.title(r'$u_{SOL}(c,h)$')
        plt.xlabel(r'$h$')
        plt.ylabel(r'$u_{SOL}(c,h)$')
        plt.legend()
        plt.sca(axs[1][0])
        for c in (0.6, 0.7, 0.8, 0.9, 0.95, 0.99):     # plots some of the e2H curves
            minmax.my_plot(lambda z: np.sqrt(minmax.e2H(c,z)),minmax.h0(c)+1e-5,np.pi-1e-5,label='c = '+str(c))
        plt.ylim(0, None)
        plt.title(r'eccentricity '+'$e_{H}(c,h)$')
        plt.xlabel(r'h')
        plt.ylabel(r'$e_{H}(c,h)$')
        plt.legend()
        plt.sca(axs[1][1])
        for c in (0.6, 0.5, 0.4, 0.3, 0.2, 0.1):              # plots some of the e2H curves
            minmax.my_plot(lambda z: np.sqrt(minmax.e2H(c,z)),max(minmax.h0(c),minmax.inv_one_minus_hcoth(1/(2*c*c)))+1e-5,np.pi-1e-5,label='c = '+str(c))
        plt.ylim(0, 1)
        plt.title(r'eccentricity '+'$e_{H}(c,h)$')
        plt.xlabel(r'h')
        plt.ylabel(r'$e_{H}(c,h)$')
        plt.legend()
        plt.show()
    
    ########################################
    elif figureId == "A8":
        fig, axs = plt.subplots(1,2,figsize=(12, 4))
        plt.sca(axs[0])
        minmax.my_plot(lambda z: minmax.eH0(z),minmax.c0s,1, label='eH0')
        minmax.my_plot(lambda z: 1/3,0,1, label='1/3')
        plt.axis([0, 1, 0, 1])
        plt.xlabel(r'c = cos($\epsilon$) = cos(obliquity)')
        plt.ylabel('e = eccentricity')
        plt.title(r'Boundaries of $e_{H}(c,h)$: $e_{H0}(c)$ ($h=h_{0}(c)$) and 1/3 ($h=π$)')
        plt.legend()
        plt.sca(axs[1])
        minmax.my_plot(lambda z: minmax.eHmin1_approx(z),0,1, label='eHmin1')
        minmax.my_plot(lambda z: minmax.eHmax_approx(z),minmax.c0max,1, label='eHmax')
        minmax.my_plot(lambda z: minmax.eHmin2_approx(z),minmax.c0min2,minmax.c0r, label='eHmin2')
        plt.axis([0, 1, 0, 1])
        plt.title(r'Extremal (min/max) values of $e_{H}(c,h)$')
        plt.xlabel(r'c = cos($\epsilon$) = cos(obliquity)')
        plt.ylabel('e = eccentricity')
        plt.legend()
        plt.show()
    
    ########################################
    elif figureId == "A9":
        fig, axs = plt.subplots(1,2,figsize=(12, 5))
        plt.sca(axs[0])
        minmax.plot_Hdomains()
        plt.plot([.9], [0.05], '*',color='r')
        plt.plot([.5], [0.5], '*',color='r')
        plt.plot([.45], [0.05], '*',color='r')
        plt.plot([.6], [0.15], '*',color='r')
        plt.plot([.6], [0.2], '*',color='r')
        plt.plot([.4], [0.35], '*',color='r')
        plt.plot([.38], [0.4], '*',color='r')
        plt.plot([.46], [0.1], '*',color='r')
        plt.plot([.4], [0.1], '*',color='r')
        plt.sca(axs[1])
        minmax.plot_Hdomains_zoomed()
        plt.show()
    
    ########################################
    elif figureId == "A10":
        fig, axs = plt.subplots(3,3,figsize=(16, 15))
        minmax.subplot_lbd_minmaxH(axs[0][0],.05,np.arccos(.9))
        minmax.subplot_lbd_minmaxH(axs[0][1],.5,np.arccos(.5))
        minmax.subplot_lbd_minmaxH(axs[0][2],.05,np.arccos(.45))
        minmax.subplot_lbd_minmaxH(axs[1][0],.15,np.arccos(.6))
        minmax.subplot_lbd_minmaxH(axs[1][1],.2,np.arccos(.6))
        minmax.subplot_lbd_minmaxH(axs[1][2],.35,np.arccos(.4))
        minmax.subplot_lbd_minmaxH(axs[2][0],.4,np.arccos(.38))
        minmax.subplot_lbd_minmaxH(axs[2][1],.1,np.arccos(.46))
        minmax.subplot_lbd_minmaxH(axs[2][2],.1,np.arccos(.4))
        plt.show()

#=========================================================================================
def main():
    figureId = sys.argv[1] if len(sys.argv) > 1 else None 
    inso.display(figureId)

if __name__ == "__main__":
    main()
