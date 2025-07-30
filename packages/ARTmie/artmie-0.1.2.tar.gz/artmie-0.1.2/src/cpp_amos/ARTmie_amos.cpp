#include <complex>
#include <cmath>
#include <limits>
#include <vector>



/** CONSTANTS */
static const double _PI_  = 3.141592653589793238462643383;
static const double HPI   = 1.570796326794896619232; //0.5*PI
static const double FPI   = 1.89769999331517738144436510577908705; //(128/PI²)^0.25
static const double SPI   = 1.9098593171027440292266051604701723444; //6/PI
static const double THPI  = 4.712388980384689857695; //1.5*PI
static const double RTPI  = 0.159154943091895336; //0.5/PI
static const double RTHPI = 1.25331413731550025; //sqrt(0.5*PI)
static const double LN2PI = 1.83787706640934548; //log(2*PI)
static const double LN10  = 2.30258509299;
static const double AIC   = 1.2655121234846453964889457971347059239; //log(sqrt(4*PI))
static const double RT2   = 1.4142135623730950488016887242096980786; //sqrt(2)
static const double DRT   = 0.7071067811865475244008443621048490393; //sqrt(0.5)
static const double RT3   = 1.7320508075688772935274463415058723669; //sqrt(3)
static const double AI0   = 0.35502805388781723926006318600418317639797917419917724058332651030081004245; // 1.0/(3^(2/3) * gamma(2/3))
static const double AIP0  = 0.25881940379280679840518356018920396347909113835493458221000181385610277267; // 1.0/(3^(1/3) * gamma(1/3))




/********************************************************************
 * ported version of the AMOS for calculating the bessel functions  *
 ********************************************************************
 * without kode==2 for exponentially scaled bessel functions,       *
 * because they are not needed for this library                     *
 ********************************************************************
 * Author: AMOS, Donald E., Sandia National Laboratories            *
 * Ported by: Metzner, Enrico P., Karlsruhe Institute of technology *
 ********************************************************************/

//integer machine constants
static const int    I1MACH[16] = {
		0, 0, 0, 0,
		32, 4, 2,
		31, 0x7fffffff, 2,
		23, -126, 127,
		53, -1022, 1023
};
//double precission machine constants
static const double D1MACH[5] = {
		std::numeric_limits<double>::min(), std::numeric_limits<double>::max(),
		std::pow(2.0,-52), std::pow(2.0,-51), std::log10(2.0)
};
static const double GLN[100] = {
		0.00000000000000000E+00, 0.00000000000000000E+00, 6.93147180559945309E-01, 1.79175946922805500E+00, 3.17805383034794562E+00,
		4.78749174278204599E+00, 6.57925121201010100E+00, 8.52516136106541430E+00, 1.06046029027452502E+01, 1.28018274800814696E+01,
		1.51044125730755153E+01, 1.75023078458738858E+01, 1.99872144956618861E+01, 2.25521638531234229E+01, 2.51912211827386815E+01,
		2.78992713838408916E+01, 3.06718601060806728E+01, 3.35050734501368889E+01, 3.63954452080330536E+01, 3.93398841871994940E+01,
		4.23356164607534850E+01, 4.53801388984769080E+01, 4.84711813518352239E+01, 5.16066755677643736E+01, 5.47847293981123192E+01,
		5.80036052229805199E+01, 6.12617017610020020E+01, 6.45575386270063311E+01, 6.78897431371815350E+01, 7.12570389671680090E+01,
		7.46582363488301644E+01, 7.80922235533153106E+01, 8.15579594561150372E+01, 8.50544670175815174E+01, 8.85808275421976788E+01,
		9.21361756036870925E+01, 9.57196945421432025E+01, 9.93306124547874269E+01, 1.02968198614513813E+02, 1.06631760260643459E+02,
		1.10320639714757395E+02, 1.14034211781461703E+02, 1.17771881399745072E+02, 1.21533081515438634E+02, 1.25317271149356895E+02,
		1.29123933639127215E+02, 1.32952575035616310E+02, 1.36802722637326368E+02, 1.40673923648234259E+02, 1.44565743946344886E+02,
		1.48477766951773032E+02, 1.52409592584497358E+02, 1.56360836303078785E+02, 1.60331128216630907E+02, 1.64320112263195181E+02,
		1.68327445448427652E+02, 1.72352797139162802E+02, 1.76395848406997352E+02, 1.80456291417543771E+02, 1.84533828861449491E+02,
		1.88628173423671591E+02, 1.92739047287844902E+02, 1.96866181672889994E+02, 2.01009316399281527E+02, 2.05168199482641199E+02,
		2.09342586752536836E+02, 2.13532241494563261E+02, 2.17736934113954227E+02, 2.21956441819130334E+02, 2.26190548323727593E+02,
		2.30439043565776952E+02, 2.34701723442818268E+02, 2.38978389561834323E+02, 2.43268849002982714E+02, 2.47572914096186884E+02,
		2.51890402209723194E+02, 2.56221135550009525E+02, 2.60564940971863209E+02, 2.64921649798552801E+02, 2.69291097651019823E+02,
		2.73673124285693704E+02, 2.78067573440366143E+02, 2.82474292687630396E+02, 2.86893133295426994E+02, 2.91323950094270308E+02,
		2.95766601350760624E+02, 3.00220948647014132E+02, 3.04686856765668715E+02, 3.09164193580146922E+02, 3.13652829949879062E+02,
		3.18152639620209327E+02, 3.22663499126726177E+02, 3.27185287703775217E+02, 3.31717887196928473E+02, 3.36261181979198477E+02,
		3.40815058870799018E+02, 3.45379407062266854E+02, 3.49954118040770237E+02, 3.54539085519440809E+02, 3.59134205369575399E+02
};
double dgamln(double x) {
	if(x<=0.0)
		return std::numeric_limits<double>::quiet_NaN();
	int ix = (int)x;
	double dx = x-ix;
	if(dx==0.0 && ix<100)
		return GLN[ix-1];
	static const double cf[22] = {
		8.33333333333333333E-02, -2.77777777777777778E-03, 7.93650793650793651E-04, -5.95238095238095238E-04, 8.41750841750841751E-04,
		-1.91752691752691753E-03, 6.41025641025641026E-03, -2.95506535947712418E-02, 1.79644372368830573E-01, -1.39243221690590112E+00,
		1.34028640441683920E+01, -1.56848284626002017E+02, 2.19310333333333333E+03, -3.61087712537249894E+04, 6.91472268851313067E+05,
		-1.52382215394074162E+07, 3.82900751391414141E+08, -1.08822660357843911E+10, 3.47320283765002252E+11, -1.23696021422692745E+13,
		4.88788064793079335E+14, -2.13203339609193739E+16
	};
	double wdtol = std::max(D1MACH[3],0.5e-18);
	double fln = std::max(3.0,std::min(D1MACH[4]*I1MACH[13],20.0))-3.0;
	int xmin = 1+(int)(1.8+0.3875*fln);
	int xinc = std::max(0,(xmin-ix));
	double xv = x+xinc;
	double rx = 1.0/xv;
	double t1 = cf[0]*rx;
	double s = t1;
	if(rx>=wdtol) {
		double sx = rx*rx;
		double tst = cf[0]*wdtol;
		for(int k=2; k<=22; k++) {
			rx *= sx;
			dx = cf[k-1]*rx;
			if(std::abs(dx)<tst) break;
			s += dx;
		}
	}
	rx = 1.0;
	for(int i=0; i<xinc; i++) {
		rx *= x+i;
	}
	t1 = std::log(xv);
	return xv*(t1-1.0)-std::log(rx)+0.5*(LN2PI-t1)+s;
}
static const double CZEROR = 0.0;
static const double CZEROI = 0.0;
static const double CONER = 1.0;
static const double CONEI = 0.0;
static const double CTWOR = 2.0;
double dsign(double dest, double src) {
	double a = std::abs(dest);
	if(src<0.0) {
		return -a;
	}
	return a;
}
double zabs(double zr, double zi) {
	double r = std::abs(zr);
	double i = std::abs(zi);
	double l = r>=i ? r : i;
	double s = r<i ? r : i;
	s /= l;
	return l*std::sqrt(1.0+s*s);
}
void zmlt(double fac1r, double fac1i, double fac2r, double fac2i, double *OUTR, double *OUTI) {
	*OUTR = fac1r*fac2r - fac1i*fac2i;
	*OUTI = fac1r*fac2i + fac1i*fac2r;
}
void zdiv(double numr, double numi, double denr, double deni, double *OUTR, double *OUTI) {
	double rm = 1.0 / zabs(denr,deni);
	double r  =  denr*rm;
	double i  = -deni*rm;
	*OUTR = (numr*r - numi*i)*rm;
	*OUTI = (numr*i + numi*r)*rm;
}
void zsqrt(double ar, double ai, double *BR, double *BI) {
	double zm = std::sqrt(zabs(ar,ai));
	if(ar==0.0) {
		if(ai==0.0) {
			*BR = 0.0;
			*BI = 0.0;
		} else {
			*BR = zm*DRT;
			*BI = (ai<0.0 ? -zm : zm)*DRT;
		}
		return;
	}
	if(ai==0.0) {
		if(ar>0.0) {
			*BR = std::sqrt(ar);
			*BI = 0.0;
		} else {
			*BR = 0.0;
			*BI = std::sqrt(-ar);
		}
		return;
	}
	double dtheta = std::atan(ai/ar);
	if(ar<0.0) dtheta += dtheta<0.0 ? _PI_ : -_PI_;
	dtheta = dtheta*0.5;
	*BR = zm*std::cos(dtheta);
	*BI = zm*std::sin(dtheta);
	return;
}
void zexp(double zr, double zi, double *OUTR, double *OUTI) {
	double e = std::exp(zr);
	*OUTR = e*std::cos(zi);
	*OUTI = e*std::sin(zi);
}
void zlog(double ar, double ai, double *BR, double *BI, int *IERR) {
	*IERR = 0;
	if(ar==0.0) {
		if(ai==0.0) {
			*IERR = 1;
			return;
		}
		*BI = HPI;
		*BR = std::log(std::abs(ai));
		if(ai<0.0) *BI = -*BI;
		return;
	}
	if(ai==0.0) {
		*BR = std::log(std::abs(ar));
		*BR = ar>0.0 ? 0.0 : _PI_;
		return;
	}
	*BR = std::log(zabs(ar,ai));
	double dtheta = std::atan(ai/ar);
	if(ar<0.0) dtheta += dtheta<0.0 ? _PI_ : -_PI_;
	*BI = dtheta;
	return;
}


void zasyi(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, double rl, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zasyi\n");
	double aa, aez, ak, ak1i, ak1r, arg, arm, atol, az, bb, bk, cki, ckr, cs1i, cs1r, \
	       cs2i, cs2r, czi, czr, dfnu, dki, dkr, dnu2, ezi, ezr, fdn, p1i, p1r, raz, \
		   rtr1, rzi, rzr, s, sgn, sqk, sti, str, s2i, s2r, tzi, tzr;
	int    i, ib, il, inu, j, jl, k, koded, m, nn;

	*NZ = 0;
	az = zabs(zr,zi);
	arm = 1000.0*D1MACH[0];
	rtr1 = std::sqrt(arm);
	il = std::min(2,n);
	dfnu = fnu + (double)(n-il);
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST
//C-----------------------------------------------------------------------
	raz = 1.0/az;
	str = zr*raz;
	sti = -zi*raz;
	ak1r = RTPI*str*raz;
	ak1i = RTPI*sti*raz;
	zsqrt(ak1r, ak1i, &ak1r, &ak1i);
	czr = zr;
	czi = zi;
	if (kode != 2) goto YI10;
	czr = CZEROR;
	czi = zi;
YI10:
	if(std::abs(czr)>elim) goto YI100;
	dnu2 = dfnu + dfnu;
	koded = 1;
	if((std::abs(czr)>alim) && (n>2)) goto YI20;
	koded = 0;
	zexp(czr, czi, &str, &sti);
	zmlt(ak1r, ak1i, str, sti, &ak1r, &ak1i);
YI20:
	fdn = 0.0;
	if (dnu2>rtr1) fdn = dnu2*dnu2;
	ezr = zr*8.0;
	ezi = zi*8.0;
//C-----------------------------------------------------------------------
//C     WHEN Z IS IMAGINARY, THE ERROR TEST MUST BE MADE RELATIVE TO THE
//C     FIRST RECIPROCAL POWER SINCE THIS IS THE LEADING TERM OF THE
//C     EXPANSION FOR THE IMAGINARY PART.
//C-----------------------------------------------------------------------
	aez = 8.0*az;
	s = tol/aez;
	jl = ((int)(rl+rl)) + 2;
	p1r = CZEROR;
	p1i = CZEROI;
	if (zi==0.0) goto YI30;
//C-----------------------------------------------------------------------
//C     CALCULATE EXP(PI*(0.5+FNU+N-IL)*I) TO MINIMIZE LOSSES OF
//C     SIGNIFICANCE WHEN FNU OR N IS LARGE
//C-----------------------------------------------------------------------
	inu = (int)fnu;
	arg = (fnu-(double)inu)*_PI_;
	inu = inu + n - il;
	ak = -std::sin(arg);
	bk =  std::cos(arg);
	if (zi < 0.0) bk = -bk;
	p1r = ak;
	p1i = bk;
	if ((inu&1)==0) goto YI30;
	p1r = -p1r;
	p1i = -p1i;
YI30:
	for(k=1; k<=il; k++) { //DO 70
		sqk = fdn - 1.0;
		atol = s*std::abs(sqk);
		sgn = 1.0;
		cs1r = CONER;
		cs1i = CONEI;
		cs2r = CONER;
		cs2i = CONEI;
		ckr = CONER;
		cki = CONEI;
		ak = 0.0;
		aa = 1.0;
		bb = aez;
		dkr = ezr;
		dki = ezi;
		for(j=1; j<=jl; j++) {
			zdiv(ckr, cki, dkr, dki, &str, &sti);
			ckr = str*sqk;
			cki = sti*sqk;
			cs2r = cs2r + ckr;
			cs2i = cs2i + cki;
			sgn = -sgn;
			cs1r = cs1r + ckr*sgn;
			cs1i = cs1i + cki*sgn;
			dkr = dkr + ezr;
			dki = dki + ezi;
			aa = aa*std::abs(sqk)/bb;
			bb = bb + aez;
			ak = ak + 8.0;
			sqk = sqk - ak;
			if (aa<=atol) goto YI50;
		} //CONTINUE 40
		goto YI110;
YI50:
		s2r = cs1r;
		s2i = cs1i;
		if (zr+zr>=elim) goto YI60;
		tzr = zr + zr;
		tzi = zi + zi;
		zexp(-tzr, -tzi, &str, &sti);
		zmlt(str, sti, p1r, p1i, &str, &sti);
		zmlt(str, sti, cs2r, cs2i, &str, &sti);
		s2r = s2r + str;
		s2i = s2i + sti;
YI60:
		fdn = fdn + 8.0*dfnu + 4.0;
		p1r = -p1r;
		p1i = -p1i;
		m = n - il + k;
		YR[m-1] = s2r*ak1r - s2i*ak1i;
		YI[m-1] = s2r*ak1i + s2i*ak1r;
	} //CONTINUE 70
	if (n<=2) return;
	nn = n;
	k = nn - 2;
	ak = (double)k;
	str = zr*raz;
	sti = -zi*raz;
	rzr = (str+str)*raz;
	rzi = (sti+sti)*raz;
	ib = 3;
	for(i=ib; i<=nn; i++) { //DO 80
		YR[k-1] = (ak+fnu)*(rzr*YR[k]-rzi*YI[k]) + YR[k+1];
		YI[k-1] = (ak+fnu)*(rzr*YI[k]+rzi*YR[k]) + YI[k+1];
		ak = ak - 1.0;
		k = k - 1;
	} //CONTINUE 80
	if (koded==0) return;
	zexp(czr, czi, &ckr, &cki);
	for(i=1; i<=nn; i++) { //DO 90
		str = YR[i-1]*ckr - YI[i-1]*cki;
		YI[i-1] = YR[i-1]*cki + YI[i-1]*ckr;
		YR[i-1] = str;
	} //CONTINUE 90
	return;
YI100:
	*NZ = -1;
	return;
YI110:
	*NZ = -2;
	return;
}
void zrati(double zr, double zi, double fnu, int n, double *CYR, double *CYI, double tol, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zrati\n");
	double ak, amagz, ap1, ap2, arg, az, cdfnui, cdfnur, dfnu, fdnu, flam, \
		   fnup, pti, ptr, p1i, p1r, p2i, p2r, rak, rap1, rho, rzi, rzr, \
		   test, test1, tti, ttr, t1i, t1r;
	int    i, id, idnu, inu, itime, k, kk, magz;

	az = zabs(zr,zi);
	inu = (int)fnu;
	idnu = inu + n - 1;
	magz = (int)az;
	amagz = (double)(magz+1);
	fdnu = (double)idnu;
	fnup = std::max(amagz,fdnu);
	id = idnu - magz - 1;
	itime = 1;
	k = 1;
	ptr = 1.0/az;
	rzr = ptr*(zr+zr)*ptr;
	rzi = -ptr*(zi+zi)*ptr;
	t1r = rzr*fnup;
	t1i = rzi*fnup;
	p2r = -t1r;
	p2i = -t1i;
	p1r = CONER;
	p1i = CONEI;
	t1r = t1r + rzr;
	t1i = t1i + rzi;
	if (id>0) id = 0;
	ap2 = zabs(p2r,p2i);
	ap1 = zabs(p1r,p1i);
//C-----------------------------------------------------------------------
//C     THE OVERFLOW TEST ON K(FNU+I-1,Z) BEFORE THE CALL TO CBKNU
//C     GUARANTEES THAT P2 IS ON SCALE. SCALE TEST1 AND ALL SUBSEQUENT
//C     P2 VALUES BY AP1 TO ENSURE THAT AN OVERFLOW DOES NOT OCCUR
//C     PREMATURELY.
//C-----------------------------------------------------------------------
	arg = (ap2+ap2)/(ap1*tol);
	test1 = std::sqrt(arg);
	test = test1;
	rap1 = 1.0/ap1;
	p1r = p1r*rap1;
	p1i = p1i*rap1;
	p2r = p2r*rap1;
	p2i = p2i*rap1;
	ap2 = ap2*rap1;
TI10:
	k = k + 1;
	ap1 = ap2;
	ptr = p2r;
	pti = p2i;
	p2r = p1r - (t1r*ptr-t1i*pti);
	p2i = p1i - (t1r*pti+t1i*ptr);
	p1r = ptr;
	p1i = pti;
	t1r = t1r + rzr;
	t1i = t1i + rzi;
	ap2 = zabs(p2r,p2i);
	if(ap1<=test) goto TI10;
	if (itime==2) goto TI20;
	ak = zabs(t1r,t1i)*0.5;
	flam = ak + std::sqrt(ak*ak-1.0);
	rho = std::min(ap2/ap1,flam);
	test = test1*std::sqrt(rho/(rho*rho-1.0));
	itime = 2;
	goto TI10;
TI20:
	kk = k + 1 - id;
	ak = (double)kk;
	t1r = ak;
	t1i = CZEROI;
	dfnu = fnu + (double)(n-1);
	p1r = 1.0/ap2;
	p1i = CZEROI;
	p2r = CZEROR;
	p2i = CZEROI;
	for(i=1; i<=kk; i++) { //DO 30
		ptr = p1r;
		pti = p1i;
		rap1 = dfnu + t1r;
		ttr = rzr*rap1;
		tti = rzi*rap1;
		p1r = (ptr*ttr-pti*tti) + p2r;
		p1i = (ptr*tti+pti*ttr) + p2i;
		p2r = ptr;
		p2i = pti;
		t1r = t1r - CONER;
	} //CONTINUE 30
	if (p1r!=CZEROR || p1i!=CZEROI) goto TI40;
	p1r = tol;
	p1i = tol;
TI40:
	zdiv(p2r, p2i, p1r, p1i, &(CYR[n-1]), &(CYI[n-1]));
	if (n==1) return;
	k = n - 1;
	ak = (double)k;
	t1r = ak;
	t1i = CZEROI;
	cdfnur = fnu*rzr;
	cdfnui = fnu*rzi;
	for(i=2; i<=n; i++) { //DO 60
		ptr = cdfnur + (t1r*rzr-t1i*rzi) + CYR[k];
		pti = cdfnui + (t1r*rzi+t1i*rzr) + CYI[k];
		ak = zabs(ptr,pti);
		if (ak!=CZEROR) goto TI50;
		ptr = tol;
		pti = tol;
		ak = tol*RT2;
TI50:
		rak = CONER/ak;
		CYR[k-1] = rak*ptr*rak;
		CYI[k-1] = -rak*pti*rak;
		t1r = t1r - CONER;
		k = k - 1;
	} //CONTINUE 60
	return;
}
void zshch(double zr, double zi, double *CSHR, double *CSHI, double *CCHR, double *CCHI) {
	//calculates sinh(z) and cosh(z)
	double sh = std::sinh(zr);
	double ch = std::cosh(zr);
	double si = std::sin(zi);
	double co = std::cos(zi);
	*CSHR = sh*co;
	*CSHI = ch*si;
	*CCHR = ch*co;
	*CCHI = sh*si;
	return;
}
void zs1s2(double zr, double zi, double *S1R, double *S1I, double *S2R, double *S2I, int *NZ, double ascle, double alim, int *IUF, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zs1s2\n");
	double aa, aln, as1, as2, c1i, c1r, s1di, s1dr;
	int    idum;

	*NZ = 0;
	as1 = zabs(*S1R,*S1I);
	as2 = zabs(*S2R,*S2I);
	if (*S1R==0.0 && *S1I==0.0) goto ZS10;
	if (as1==0.0) goto ZS10;
	aln = -zr - zr + std::log(as1);
	s1dr = *S1R;
	s1di = *S1I;
	*S1R = CZEROR;
	*S1I = CZEROI;
	as1 = CZEROR;
	if (aln<(-alim)) goto ZS10;
	zlog(s1dr, s1di, &c1r, &c1i, &idum);
	c1r = c1r - zr - zr;
	c1i = c1i - zi - zi;
	zexp(c1r, c1i, S1R, S1I);
	as1 = zabs(*S1R,*S1I);
	*IUF = *IUF + 1;
ZS10:
	aa = std::max(as1,as2);
	if (aa>ascle) return;
	*S1R = CZEROR;
	*S1I = CZEROI;
	*S2R = CZEROR;
	*S2I = CZEROI;
	*NZ = 1;
	*IUF = 0;
	return;
}
void zuchk(double yr, double yi, int *NZ, double ascle, double tol, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zuchk\n");
	double ss, st, wr, wi;

	*NZ = 0;
	wr = std::abs(yr);
	wi = std::abs(yi);
	st = std::min(wr,wi);
	if (st>ascle) return;
	ss = std::max(wr,wi);
	st = st/tol;
	if (ss<st) *NZ = 1;
	return;
}
static const double AR[14] = {
		1.00000000000000000E+00, 1.04166666666666667E-01, 8.35503472222222222E-02, 1.28226574556327160E-01, 2.91849026464140464E-01,
		8.81627267443757652E-01, 3.32140828186276754E+00, 1.49957629868625547E+01, 7.89230130115865181E+01, 4.74451538868264323E+02,
		3.20749009089066193E+03, 2.40865496408740049E+04, 1.98923119169509794E+05, 1.79190200777534383E+06
};
static const double BR[14] = {
		1.00000000000000000E+00, -1.45833333333333333E-01, -9.87413194444444444E-02, -1.43312053915895062E-01, -3.17227202678413548E-01,
		-9.42429147957120249E-01, -3.51120304082635426E+00, -1.57272636203680451E+01, -8.22814390971859444E+01, -4.92355370523670524E+02,
		-3.31621856854797251E+03, -2.48276742452085896E+04, -2.04526587315129788E+05, -1.83844491706820990E+06
};
static const double CR[105] = {
		1.00000000000000000E+00, -2.08333333333333333E-01, 1.25000000000000000E-01, 3.34201388888888889E-01, -4.01041666666666667E-01,
		7.03125000000000000E-02, -1.02581259645061728E+00, 1.84646267361111111E+00, -8.91210937500000000E-01, 7.32421875000000000E-02,
		4.66958442342624743E+00, -1.12070026162229938E+01, 8.78912353515625000E+00, -2.36408691406250000E+00, 1.12152099609375000E-01,
		-2.82120725582002449E+01, 8.46362176746007346E+01, -9.18182415432400174E+01, 4.25349987453884549E+01, -7.36879435947963170E+00,
		2.27108001708984375E-01, 2.12570130039217123E+02, -7.65252468141181642E+02, 1.05999045252799988E+03, -6.99579627376132541E+02,
		2.18190511744211590E+02, -2.64914304869515555E+01, 5.72501420974731445E-01, -1.91945766231840700E+03, 8.06172218173730938E+03,
		-1.35865500064341374E+04, 1.16553933368645332E+04, -5.30564697861340311E+03, 1.20090291321635246E+03, -1.08090919788394656E+02,
		1.72772750258445740E+00, 2.02042913309661486E+04, -9.69805983886375135E+04, 1.92547001232531532E+05, -2.03400177280415534E+05,
		1.22200464983017460E+05, -4.11926549688975513E+04, 7.10951430248936372E+03, -4.93915304773088012E+02, 6.07404200127348304E+00,
		-2.42919187900551333E+05, 1.31176361466297720E+06, -2.99801591853810675E+06, 3.76327129765640400E+06, -2.81356322658653411E+06,
		1.26836527332162478E+06, -3.31645172484563578E+05, 4.52187689813627263E+04, -2.49983048181120962E+03, 2.43805296995560639E+01,
		3.28446985307203782E+06, -1.97068191184322269E+07, 5.09526024926646422E+07, -7.41051482115326577E+07, 6.63445122747290267E+07,
		-3.75671766607633513E+07, 1.32887671664218183E+07, -2.78561812808645469E+06, 3.08186404612662398E+05, -1.38860897537170405E+04,
		1.10017140269246738E+02, -4.93292536645099620E+07, 3.25573074185765749E+08, -9.39462359681578403E+08, 1.55359689957058006E+09,
		-1.62108055210833708E+09, 1.10684281682301447E+09, -4.95889784275030309E+08, 1.42062907797533095E+08, -2.44740627257387285E+07,
		2.24376817792244943E+06, -8.40054336030240853E+04, 5.51335896122020586E+02, 8.14789096118312115E+08, -5.86648149205184723E+09,
		1.86882075092958249E+10, -3.46320433881587779E+10, 4.12801855797539740E+10, -3.30265997498007231E+10, 1.79542137311556001E+10,
		-6.56329379261928433E+09, 1.55927986487925751E+09, -2.25105661889415278E+08, 1.73951075539781645E+07, -5.49842327572288687E+05,
		3.03809051092238427E+03, -1.46792612476956167E+10, 1.14498237732025810E+11, -3.99096175224466498E+11, 8.19218669548577329E+11,
		-1.09837515608122331E+12, 1.00815810686538209E+12, -6.45364869245376503E+11, 2.87900649906150589E+11, -8.78670721780232657E+10,
		1.76347306068349694E+10, -2.16716498322379509E+09, 1.43157876718888981E+08, -3.87183344257261262E+06, 1.82577554742931747E+04
};
static const double ALFA[180] = {
		-4.44444444444444444E-03, -9.22077922077922078E-04, -8.84892884892884893E-05, 1.65927687832449737E-04, 2.46691372741792910E-04,
		2.65995589346254780E-04, 2.61824297061500945E-04, 2.48730437344655609E-04, 2.32721040083232098E-04, 2.16362485712365082E-04,
		2.00738858762752355E-04, 1.86267636637545172E-04, 1.73060775917876493E-04, 1.61091705929015752E-04, 1.50274774160908134E-04,
		1.40503497391269794E-04, 1.31668816545922806E-04, 1.23667445598253261E-04, 1.16405271474737902E-04, 1.09798298372713369E-04,
		1.03772410422992823E-04, 9.82626078369363448E-05, 9.32120517249503256E-05, 8.85710852478711718E-05, 8.42963105715700223E-05,
		8.03497548407791151E-05, 7.66981345359207388E-05, 7.33122157481777809E-05, 7.01662625163141333E-05, 6.72375633790160292E-05,
		6.93735541354588974E-04, 2.32241745182921654E-04, -1.41986273556691197E-05, -1.16444931672048640E-04, -1.50803558053048762E-04,
		-1.55121924918096223E-04, -1.46809756646465549E-04, -1.33815503867491367E-04, -1.19744975684254051E-04, -1.06184319207974020E-04,
		-9.37699549891194492E-05, -8.26923045588193274E-05, -7.29374348155221211E-05, -6.44042357721016283E-05, -5.69611566009369048E-05,
		-5.04731044303561628E-05, -4.48134868008882786E-05, -3.98688727717598864E-05, -3.55400532972042498E-05, -3.17414256609022480E-05,
		-2.83996793904174811E-05, -2.54522720634870566E-05, -2.28459297164724555E-05, -2.05352753106480604E-05, -1.84816217627666085E-05,
		-1.66519330021393806E-05, -1.50179412980119482E-05, -1.35554031379040526E-05, -1.22434746473858131E-05, -1.10641884811308169E-05,
		-3.54211971457743841E-04, -1.56161263945159416E-04, 3.04465503594936410E-05, 1.30198655773242693E-04, 1.67471106699712269E-04,
		1.70222587683592569E-04, 1.56501427608594704E-04, 1.36339170977445120E-04, 1.14886692029825128E-04, 9.45869093034688111E-05,
		7.64498419250898258E-05, 6.07570334965197354E-05, 4.74394299290508799E-05, 3.62757512005344297E-05, 2.69939714979224901E-05,
		1.93210938247939253E-05, 1.30056674793963203E-05, 7.82620866744496661E-06, 3.59257485819351583E-06, 1.44040049814251817E-07,
		-2.65396769697939116E-06, -4.91346867098485910E-06, -6.72739296091248287E-06, -8.17269379678657923E-06, -9.31304715093561232E-06,
		-1.02011418798016441E-05, -1.08805962510592880E-05, -1.13875481509603555E-05, -1.17519675674556414E-05, -1.19987364870944141E-05,
		3.78194199201772914E-04, 2.02471952761816167E-04, -6.37938506318862408E-05, -2.38598230603005903E-04, -3.10916256027361568E-04,
		-3.13680115247576316E-04, -2.78950273791323387E-04, -2.28564082619141374E-04, -1.75245280340846749E-04, -1.25544063060690348E-04,
		-8.22982872820208365E-05, -4.62860730588116458E-05, -1.72334302366962267E-05, 5.60690482304602267E-06, 2.31395443148286800E-05,
		3.62642745856793957E-05, 4.58006124490188752E-05, 5.24595294959114050E-05, 5.68396208545815266E-05, 5.94349820393104052E-05,
		6.06478527578421742E-05, 6.08023907788436497E-05, 6.01577894539460388E-05, 5.89199657344698500E-05, 5.72515823777593053E-05,
		5.52804375585852577E-05, 5.31063773802880170E-05, 5.08069302012325706E-05, 4.84418647620094842E-05, 4.60568581607475370E-05,
		-6.91141397288294174E-04, -4.29976633058871912E-04, 1.83067735980039018E-04, 6.60088147542014144E-04, 8.75964969951185931E-04,
		8.77335235958235514E-04, 7.49369585378990637E-04, 5.63832329756980918E-04, 3.68059319971443156E-04, 1.88464535514455599E-04,
		3.70663057664904149E-05, -8.28520220232137023E-05, -1.72751952869172998E-04, -2.36314873605872983E-04, -2.77966150694906658E-04,
		-3.02079514155456919E-04, -3.12594712643820127E-04, -3.12872558758067163E-04, -3.05678038466324377E-04, -2.93226470614557331E-04,
		-2.77255655582934777E-04, -2.59103928467031709E-04, -2.39784014396480342E-04, -2.20048260045422848E-04, -2.00443911094971498E-04,
		-1.81358692210970687E-04, -1.63057674478657464E-04, -1.45712672175205844E-04, -1.29425421983924587E-04, -1.14245691942445952E-04,
		1.92821964248775885E-03, 1.35592576302022234E-03, -7.17858090421302995E-04, -2.58084802575270346E-03, -3.49271130826168475E-03,
		-3.46986299340960628E-03, -2.82285233351310182E-03, -1.88103076404891354E-03, -8.89531718383947600E-04, 3.87912102631035228E-06,
		7.28688540119691412E-04, 1.26566373053457758E-03, 1.62518158372674427E-03, 1.83203153216373172E-03, 1.91588388990527909E-03,
		1.90588846755546138E-03, 1.82798982421825727E-03, 1.70389506421121530E-03, 1.55097127171097686E-03, 1.38261421852276159E-03,
		1.20881424230064774E-03, 1.03676532638344962E-03, 8.71437918068619115E-04, 7.16080155297701002E-04, 5.72637002558129372E-04,
		4.42089819465802277E-04, 3.24724948503090564E-04, 2.20342042730246599E-04, 1.28412898401353882E-04, 4.82005924552095464E-05
};
static const double BETA[210] = {
		1.79988721413553309E-02, 5.59964911064388073E-03, 2.88501402231132779E-03, 1.80096606761053941E-03, 1.24753110589199202E-03,
		9.22878876572938311E-04, 7.14430421727287357E-04, 5.71787281789704872E-04, 4.69431007606481533E-04, 3.93232835462916638E-04,
		3.34818889318297664E-04, 2.88952148495751517E-04, 2.52211615549573284E-04, 2.22280580798883327E-04, 1.97541838033062524E-04,
		1.76836855019718004E-04, 1.59316899661821081E-04, 1.44347930197333986E-04, 1.31448068119965379E-04, 1.20245444949302884E-04,
		1.10449144504599392E-04, 1.01828770740567258E-04, 9.41998224204237509E-05, 8.74130545753834437E-05, 8.13466262162801467E-05,
		7.59002269646219339E-05, 7.09906300634153481E-05, 6.65482874842468183E-05, 6.25146958969275078E-05, 5.88403394426251749E-05,
		-1.49282953213429172E-03, -8.78204709546389328E-04, -5.02916549572034614E-04, -2.94822138512746025E-04, -1.75463996970782828E-04,
		-1.04008550460816434E-04, -5.96141953046457895E-05, -3.12038929076098340E-05, -1.26089735980230047E-05, -2.42892608575730389E-07,
		8.05996165414273571E-06, 1.36507009262147391E-05, 1.73964125472926261E-05, 1.98672978842133780E-05, 2.14463263790822639E-05,
		2.23954659232456514E-05, 2.28967783814712629E-05, 2.30785389811177817E-05, 2.30321976080909144E-05, 2.28236073720348722E-05,
		2.25005881105292418E-05, 2.20981015361991429E-05, 2.16418427448103905E-05, 2.11507649256220843E-05, 2.06388749782170737E-05,
		2.01165241997081666E-05, 1.95913450141179244E-05, 1.90689367910436740E-05, 1.85533719641636667E-05, 1.80475722259674218E-05,
		5.52213076721292790E-04, 4.47932581552384646E-04, 2.79520653992020589E-04, 1.52468156198446602E-04, 6.93271105657043598E-05,
		1.76258683069991397E-05, -1.35744996343269136E-05, -3.17972413350427135E-05, -4.18861861696693365E-05, -4.69004889379141029E-05,
		-4.87665447413787352E-05, -4.87010031186735069E-05, -4.74755620890086638E-05, -4.55813058138628452E-05, -4.33309644511266036E-05,
		-4.09230193157750364E-05, -3.84822638603221274E-05, -3.60857167535410501E-05, -3.37793306123367417E-05, -3.15888560772109621E-05,
		-2.95269561750807315E-05, -2.75978914828335759E-05, -2.58006174666883713E-05, -2.41308356761280200E-05, -2.25823509518346033E-05,
		-2.11479656768912971E-05, -1.98200638885294927E-05, -1.85909870801065077E-05, -1.74532699844210224E-05, -1.63997823854497997E-05,
		-4.74617796559959808E-04, -4.77864567147321487E-04, -3.20390228067037603E-04, -1.61105016119962282E-04, -4.25778101285435204E-05,
		3.44571294294967503E-05, 7.97092684075674924E-05, 1.03138236708272200E-04, 1.12466775262204158E-04, 1.13103642108481389E-04,
		1.08651634848774268E-04, 1.01437951597661973E-04, 9.29298396593363896E-05, 8.40293133016089978E-05, 7.52727991349134062E-05,
		6.69632521975730872E-05, 5.92564547323194704E-05, 5.22169308826975567E-05, 4.58539485165360646E-05, 4.01445513891486808E-05,
		3.50481730031328081E-05, 3.05157995034346659E-05, 2.64956119950516039E-05, 2.29363633690998152E-05, 1.97893056664021636E-05,
		1.70091984636412623E-05, 1.45547428261524004E-05, 1.23886640995878413E-05, 1.04775876076583236E-05, 8.79179954978479373E-06,
		7.36465810572578444E-04, 8.72790805146193976E-04, 6.22614862573135066E-04, 2.85998154194304147E-04, 3.84737672879366102E-06,
		-1.87906003636971558E-04, -2.97603646594554535E-04, -3.45998126832656348E-04, -3.53382470916037712E-04, -3.35715635775048757E-04,
		-3.04321124789039809E-04, -2.66722723047612821E-04, -2.27654214122819527E-04, -1.89922611854562356E-04, -1.55058918599093870E-04,
		-1.23778240761873630E-04, -9.62926147717644187E-05, -7.25178327714425337E-05, -5.22070028895633801E-05, -3.50347750511900522E-05,
		-2.06489761035551757E-05, -8.70106096849767054E-06, 1.13698686675100290E-06, 9.16426474122778849E-06, 1.56477785428872620E-05,
		2.08223629482466847E-05, 2.48923381004595156E-05, 2.80340509574146325E-05, 3.03987774629861915E-05, 3.21156731406700616E-05,
		-1.80182191963885708E-03, -2.43402962938042533E-03, -1.83422663549856802E-03, -7.62204596354009765E-04, 2.39079475256927218E-04,
		9.49266117176881141E-04, 1.34467449701540359E-03, 1.48457495259449178E-03, 1.44732339830617591E-03, 1.30268261285657186E-03,
		1.10351597375642682E-03, 8.86047440419791759E-04, 6.73073208165665473E-04, 4.77603872856582378E-04, 3.05991926358789362E-04,
		1.60315694594721630E-04, 4.00749555270613286E-05, -5.66607461635251611E-05, -1.32506186772982638E-04, -1.90296187989614057E-04,
		-2.32811450376937408E-04, -2.62628811464668841E-04, -2.82050469867598672E-04, -2.93081563192861167E-04, -2.97435962176316616E-04,
		-2.96557334239348078E-04, -2.91647363312090861E-04, -2.83696203837734166E-04, -2.73512317095673346E-04, -2.61750155806768580E-04,
		6.38585891212050914E-03, 9.62374215806377941E-03, 7.61878061207001043E-03, 2.83219055545628054E-03, -2.09841352012720090E-03,
		-5.73826764216626498E-03, -7.70804244495414620E-03, -8.21011692264844401E-03, -7.65824520346905413E-03, -6.47209729391045177E-03,
		-4.99132412004966473E-03, -3.45612289713133280E-03, -2.01785580014170775E-03, -7.59430686781961401E-04, 2.84173631523859138E-04,
		1.10891667586337403E-03, 1.72901493872728771E-03, 2.16812590802684701E-03, 2.45357710494539735E-03, 2.61281821058334862E-03,
		2.67141039656276912E-03, 2.65203073395980430E-03, 2.57411652877287315E-03, 2.45389126236094427E-03, 2.30460058071795494E-03,
		2.13684837686712662E-03, 1.95896528478870911E-03, 1.77737008679454412E-03, 1.59690280765839059E-03, 1.42111975664438546E-03
};
static const double GAMA[30] = {
		6.29960524947436582E-01, 2.51984209978974633E-01, 1.54790300415655846E-01, 1.10713062416159013E-01, 8.57309395527394825E-02,
		6.97161316958684292E-02, 5.86085671893713576E-02, 5.04698873536310685E-02, 4.42600580689154809E-02, 3.93720661543509966E-02,
		3.54283195924455368E-02, 3.21818857502098231E-02, 2.94646240791157679E-02, 2.71581677112934479E-02, 2.51768272973861779E-02,
		2.34570755306078891E-02, 2.19508390134907203E-02, 2.06210828235646240E-02, 1.94388240897880846E-02, 1.83810633800683158E-02,
		1.74293213231963172E-02, 1.65685837786612353E-02, 1.57865285987918445E-02, 1.50729501494095594E-02, 1.44193250839954639E-02,
		1.38184805735341786E-02, 1.32643378994276568E-02, 1.27517121970498651E-02, 1.22761545318762767E-02, 1.18338262398482403E-02
};
void zunhj(double zr, double zi, double fnu, int ipmtr, double tol, double *PHIR, double *PHII, double *ARGR, double *ARGI, \
           double *ZETA1R, double *ZETA1I, double *ZETA2R, double *ZETA2I, double *ASUMR, double *ASUMI, double *BSUMR, double *BSUMI, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zunhj\n");
	double ac, ang, atol, aw2, azth, btol, fn13, fn23, pp, przthi, przthr, ptfni, ptfnr, raw, raw2, \
		   razth, rfnu, rfnu2, rfn13, rtzti, rtztr, rzthi, rzthr, sti, str, sumai, sumar, sumbi, sumbr, \
		   test, tfni, tfnr, tzai, tzar, t2i, t2r, wi, wr, w2i, w2r, zai, zar, zbi, zbr, \
		   zci, zcr, zetai, zetar, zthi, zthr;
	double ap[30], cri[14], crr[14], dri[14], drr[14], pi[30], pr[30], upi[14], upr[14];
	int    ias, ibs, is, j, jr, ju, k, kmax, kp1, ks, l, lr, lrp1, l1, l2, m, idum;

	rfnu = 1.0/fnu;
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST (Z/FNU TOO SMALL)
//C-----------------------------------------------------------------------
	test = 1000.0*D1MACH[0];
	ac = fnu*test;
	if (std::abs(zr)>ac || std::abs(zi)>ac) goto HJ15;
	*ZETA1R = 2.0*std::abs(std::log(test))+fnu;
	*ZETA1I = 0.0;
	*ZETA2R = fnu;
	*ZETA2I = 0.0;
	*PHIR = 1.0;
	*PHII = 0.0;
	*ARGR = 1.0;
	*ARGI = 0.0;
	return;
HJ15:
	zbr = zr*rfnu;
	zbi = zi*rfnu;
	rfnu2 = rfnu*rfnu;
//C-----------------------------------------------------------------------
//C     COMPUTE IN THE FOURTH QUADRANT
//C-----------------------------------------------------------------------
	fn13 = std::cbrt(fnu); //FNU**EX1
	fn23 = fn13*fn13;
	rfn13 = 1.0/fn13;
	w2r = CONER - zbr*zbr + zbi*zbi;
	w2i = CONEI - zbr*zbi - zbr*zbi;
	aw2 = zabs(w2r,w2i);
	if (aw2>0.25) goto HJ130;
//C-----------------------------------------------------------------------
//C     POWER SERIES FOR CABS(W2).LE.0.25D0
//C-----------------------------------------------------------------------
	k = 1;
	pr[0] = CONER;
	pi[0] = CONEI;
	sumar = GAMA[0];
	sumai = CZEROI;
	ap[0] = 1.0;
	if (aw2<tol) goto HJ20;
	for(k=2; k<=30; k++) { //DO 10
		pr[k-1] = pr[k-2]*w2r - pi[k-2]*w2i;
		pi[k-1] = pr[k-2]*w2i + pi[k-2]*w2r;
		sumar = sumar + pr[k-1]*GAMA[k-1];
		sumai = sumai + pi[k-1]*GAMA[k-1];
		ap[k-1] = ap[k-2]*aw2;
		if (ap[k-1]<tol) goto HJ20;
	} //CONTINUE 10
	k = 30;
HJ20:
	kmax = k;
	zetar = w2r*sumar - w2i*sumai;
	zetai = w2r*sumai + w2i*sumar;
	*ARGR = zetar*fn23;
	*ARGI = zetai*fn23;
	zsqrt(sumar, sumai, &zar, &zai);
	zsqrt(w2r, w2i, &str, &sti);
	*ZETA2R = str*fnu;
	*ZETA2I = sti*fnu;
	str = CONER + 2.0*(zetar*zar-zetai*zai)/3.0;
	sti = CONEI + 2.0*(zetar*zai+zetai*zar)/3.0;
	*ZETA1R = str*(*ZETA2R) - sti*(*ZETA2I);
	*ZETA1I = str*(*ZETA2I) + sti*(*ZETA2R);
	zar = zar + zar;
	zai = zai + zai;
	zsqrt(zar, zai, &str, &sti);
	*PHIR = str*rfn13;
	*PHII = sti*rfn13;
	if (ipmtr==1) goto HJ120;
//C-----------------------------------------------------------------------
//C     SUM SERIES FOR ASUM AND BSUM
//C-----------------------------------------------------------------------
	sumbr = CZEROR;
	sumbi = CZEROI;
	for(k=1; k<=kmax; k++) { //DO 30
		sumbr = sumbr + pr[k-1]*BETA[k-1];
		sumbi = sumbi + pi[k-1]*BETA[k-1];
	} //CONTINUE 30
	*ASUMR = CZEROR;
	*ASUMI = CZEROI;
	*BSUMR = sumbr;
	*BSUMI = sumbi;
	l1 = 0;
	l2 = 30;
	btol = tol*(std::abs(*BSUMR)+std::abs(*BSUMI));
	atol = tol;
	pp = 1.0;
	ias = 0;
	ibs = 0;
	if (rfnu2<tol) goto HJ110;
	for(is=2; is<=7; is++) { //DO 100
		atol = atol/rfnu2;
		pp = pp*rfnu2;
		if (ias==1) goto HJ60;
		sumar = CZEROR;
		sumai = CZEROI;
		for(k=1; k<=kmax; k++) { //DO 40
			m = l1 + k;
			sumar = sumar + pr[k-1]*ALFA[m-1];
			sumai = sumai + pi[k-1]*ALFA[m-1];
			if (ap[k-1]<atol) goto HJ50;
		} //CONTINUE 40
HJ50:
		*ASUMR = *ASUMR + sumar*pp;
		*ASUMI = *ASUMI + sumai*pp;
		if (pp<tol) ias = 1;
HJ60:
		if (ibs==1) goto HJ90;
		sumbr = CZEROR;
		sumbi = CZEROI;
		for(k=1; k<=kmax; k++) { //DO 70
			m = l2 + k;
			sumbr = sumbr + pr[k-1]*BETA[m-1];
			sumbi = sumbi + pi[k-1]*BETA[m-1];
			if(ap[k-1]<atol) goto HJ80;
		} //CONTINUE 70
HJ80:
		*BSUMR = *BSUMR + sumbr*pp;
		*BSUMI = *BSUMI + sumbi*pp;
		if(pp<btol) ibs = 1;
HJ90:
		if (ias==1 && ibs==1) goto HJ110;
		l1 = l1 + 30;
		l2 = l2 + 30;
	} //CONTINUE 100
HJ110:
	*ASUMR = *ASUMR + CONER;
	pp = rfnu*rfn13;
	*BSUMR = *BSUMR*pp;
	*BSUMI = *BSUMI*pp;
HJ120:
	return;
//C-----------------------------------------------------------------------
//C     CABS(W2).GT.0.25D0
//C-----------------------------------------------------------------------
HJ130:
	zsqrt(w2r, w2i, &wr, &wi);
	if(wr<0.0) wr = 0.0;
	if(wi<0.0) wi = 0.0;
	str = CONER + wr;
	sti = wi;
	zdiv(str, sti, zbr, zbi, &zar, &zai);
	zlog(zar, zai, &zcr, &zci, &idum);
	if(zci<0.0) zci = 0.0;
	if(zci>HPI) zci = HPI;
	if(zcr<0.0) zcr = 0.0;
	zthr = (zcr-wr)*1.5;
	zthi = (zci-wi)*1.5;
	*ZETA1R = zcr*fnu;
	*ZETA1I = zci*fnu;
	*ZETA2R = wr*fnu;
	*ZETA2I = wi*fnu;
	azth = zabs(zthr,zthi);
	ang = THPI;
	if(zthr>=0.0 && zthi<0.0) goto HJ140;
	ang = HPI;
	if(zthr==0.0) goto HJ140;
	ang = std::atan(zthi/zthr);
	if(zthr<0.0) ang = ang + _PI_;
HJ140:
	pp = std::cbrt(azth); pp *= pp; //AZTH**EX2;
	ang = 2.0*ang/3.0;
	zetar = pp*std::cos(ang);
	zetai = pp*std::sin(ang);
	if(zetai<0.0) zetai = 0.0;
	*ARGR = zetar*fn23;
	*ARGI = zetai*fn23;
	zdiv(zthr, zthi, zetar, zetai, &rtztr, &rtzti);
	zdiv(rtztr, rtzti, wr, wi, &zar, &zai);
	tzar = zar + zar;
	tzai = zai + zai;
	zsqrt(tzar, tzai, &str, &sti);
	*PHIR = str*rfn13;
	*PHII = sti*rfn13;
	if(ipmtr==1) goto HJ120;
	raw = 1.0/std::sqrt(aw2);
	str = wr*raw;
	sti = -wi*raw;
	tfnr = str*rfnu*raw;
	tfni = sti*rfnu*raw;
	razth = 1.0/azth;
	str = zthr*razth;
	sti = -zthi*razth;
	rzthr = str*razth*rfnu;
	rzthi = sti*razth*rfnu;
	zcr = rzthr*AR[1];
	zci = rzthi*AR[1];
	raw2 = 1.0/aw2;
	str = w2r*raw2;
	sti = -w2i*raw2;
	t2r = str*raw2;
	t2i = sti*raw2;
	str = t2r*CR[1] + CR[2];
	sti = t2i*CR[1];
	upr[1] = str*tfnr - sti*tfni;
	upi[1] = str*tfni + sti*tfnr;
	*BSUMR = upr[1] + zcr;
	*BSUMI = upi[1] + zci;
	*ASUMR = CZEROR;
	*ASUMI = CZEROI;
	if(rfnu<tol) goto HJ220;
	przthr = rzthr;
	przthi = rzthi;
	ptfnr = tfnr;
	ptfni = tfni;
	upr[0] = CONER;
	upi[0] = CONEI;
	pp = 1.0;
	btol = tol*(std::abs(*BSUMR)+std::abs(*BSUMI));
	ks = 0;
	kp1 = 2;
	l = 3;
	ias = 0;
	ibs = 0;
	for(lr=2; lr<=12; lr+=2) { //DO 210
		lrp1 = lr + 1;
//C-----------------------------------------------------------------------
//C     COMPUTE TWO ADDITIONAL CR, DR, AND UP FOR TWO MORE TERMS IN
//C     NEXT SUMA AND SUMB
//C-----------------------------------------------------------------------
		for(k=lr; k<=lrp1; k++) { //DO 160
			ks = ks + 1;
			kp1 = kp1 + 1;
			l = l + 1;
			zar = CR[l-1];
			zai = CZEROI;
			for(j=2; j<=kp1; j++) { //DO 150
				l = l + 1;
				str = zar*t2r - t2i*zai + CR[l-1];
				zai = zar*t2i + zai*t2r;
				zar = str;
			} //CONTINUE 150
			str = ptfnr*tfnr - ptfni*tfni;
			ptfni = ptfnr*tfni + ptfni*tfnr;
			ptfnr = str;
			upr[kp1-1] = ptfnr*zar - ptfni*zai;
			upi[kp1-1] = ptfni*zar + ptfnr*zai;
			crr[ks-1] = przthr*BR[ks];
			cri[ks-1] = przthi*BR[ks];
			str = przthr*rzthr - przthi*rzthi;
			przthi = przthr*rzthi + przthi*rzthr;
			przthr = str;
			drr[ks-1] = przthr*AR[ks+1];
			dri[ks-1] = przthi*AR[ks+1];
		} //CONTINUE 160
		pp = pp*rfnu2;
		if(ias==1) goto HJ180;
		sumar = upr[lrp1-1];
		sumai = upi[lrp1-1];
		ju = lrp1;
		for(jr=1; jr<=lr; jr++) { //DO 170
			ju = ju - 1;
			sumar = sumar + crr[jr-1]*upr[ju-1] - cri[jr-1]*upi[ju-1];
			sumai = sumai + crr[jr-1]*upi[ju-1] + cri[jr-1]*upr[ju-1];
		} //CONTINUE 170
		*ASUMR = *ASUMR + sumar;
		*ASUMI = *ASUMI + sumai;
		test = std::abs(sumar) + std::abs(sumai);
		if(pp<tol && test<tol) ias = 1;
HJ180:
		if(ibs==1) goto HJ200;
		sumbr = upr[lr+1] + upr[lrp1-1]*zcr - upi[lrp1-1]*zci;
		sumbi = upi[lr+1] + upr[lrp1-1]*zci + upi[lrp1-1]*zcr;
		ju = lrp1;
		for(jr=1; jr<=lr; jr++) { //DO 190
			ju = ju - 1;
			sumbr = sumbr + drr[jr-1]*upr[ju-1] - dri[jr-1]*upi[ju-1];
			sumbi = sumbi + drr[jr-1]*upi[ju-1] + dri[jr-1]*upr[ju-1];
		} //CONTINUE 190
		*BSUMR = *BSUMR + sumbr;
		*BSUMI = *BSUMI + sumbi;
		test = std::abs(sumbr) + std::abs(sumbi);
		if(pp<btol && test<btol) ibs = 1;
HJ200:
		if(ias==1 && ibs==1) goto HJ220;
	} //CONTINUE 210
HJ220:
	*ASUMR = *ASUMR + CONER;
	str = -*BSUMR*rfn13;
	sti = -*BSUMI*rfn13;
	zdiv(str, sti, rtztr, rtzti, BSUMR, BSUMI);
	goto HJ120;
}
static const double C[120] = {
		1.00000000000000000E+00, -2.08333333333333333E-01, 1.25000000000000000E-01, 3.34201388888888889E-01, -4.01041666666666667E-01,
		7.03125000000000000E-02, -1.02581259645061728E+00, 1.84646267361111111E+00, -8.91210937500000000E-01, 7.32421875000000000E-02,
		4.66958442342624743E+00, -1.12070026162229938E+01, 8.78912353515625000E+00, -2.36408691406250000E+00, 1.12152099609375000E-01,
		-2.82120725582002449E+01, 8.46362176746007346E+01, -9.18182415432400174E+01, 4.25349987453884549E+01, -7.36879435947963170E+00,
		2.27108001708984375E-01, 2.12570130039217123E+02, -7.65252468141181642E+02, 1.05999045252799988E+03, -6.99579627376132541E+02,
		2.18190511744211590E+02, -2.64914304869515555E+01, 5.72501420974731445E-01, -1.91945766231840700E+03, 8.06172218173730938E+03,
		-1.35865500064341374E+04, 1.16553933368645332E+04, -5.30564697861340311E+03, 1.20090291321635246E+03, -1.08090919788394656E+02,
		1.72772750258445740E+00, 2.02042913309661486E+04, -9.69805983886375135E+04, 1.92547001232531532E+05, -2.03400177280415534E+05,
		1.22200464983017460E+05, -4.11926549688975513E+04, 7.10951430248936372E+03, -4.93915304773088012E+02, 6.07404200127348304E+00,
		-2.42919187900551333E+05, 1.31176361466297720E+06, -2.99801591853810675E+06, 3.76327129765640400E+06, -2.81356322658653411E+06,
		1.26836527332162478E+06, -3.31645172484563578E+05, 4.52187689813627263E+04, -2.49983048181120962E+03, 2.43805296995560639E+01,
		3.28446985307203782E+06, -1.97068191184322269E+07, 5.09526024926646422E+07, -7.41051482115326577E+07, 6.63445122747290267E+07,
		-3.75671766607633513E+07, 1.32887671664218183E+07, -2.78561812808645469E+06, 3.08186404612662398E+05, -1.38860897537170405E+04,
		1.10017140269246738E+02, -4.93292536645099620E+07, 3.25573074185765749E+08, -9.39462359681578403E+08, 1.55359689957058006E+09,
		-1.62108055210833708E+09, 1.10684281682301447E+09, -4.95889784275030309E+08, 1.42062907797533095E+08, -2.44740627257387285E+07,
		2.24376817792244943E+06, -8.40054336030240853E+04, 5.51335896122020586E+02, 8.14789096118312115E+08, -5.86648149205184723E+09,
		1.86882075092958249E+10, -3.46320433881587779E+10, 4.12801855797539740E+10, -3.30265997498007231E+10, 1.79542137311556001E+10,
		-6.56329379261928433E+09, 1.55927986487925751E+09, -2.25105661889415278E+08, 1.73951075539781645E+07, -5.49842327572288687E+05,
		3.03809051092238427E+03, -1.46792612476956167E+10, 1.14498237732025810E+11, -3.99096175224466498E+11, 8.19218669548577329E+11,
		-1.09837515608122331E+12, 1.00815810686538209E+12, -6.45364869245376503E+11, 2.87900649906150589E+11, -8.78670721780232657E+10,
		1.76347306068349694E+10, -2.16716498322379509E+09, 1.43157876718888981E+08, -3.87183344257261262E+06, 1.82577554742931747E+04,
		2.86464035717679043E+11, -2.40629790002850396E+12, 9.10934118523989896E+12, -2.05168994109344374E+13, 3.05651255199353206E+13,
		-3.16670885847851584E+13, 2.33483640445818409E+13, -1.23204913055982872E+13, 4.61272578084913197E+12, -1.19655288019618160E+12,
		2.05914503232410016E+11, -2.18229277575292237E+10, 1.24700929351271032E+09, -2.91883881222208134E+07, 1.18838426256783253E+05
};
void zunik(double zr, double zi, double fnu, int ikflg, int ipmtr, double tol, int *INIT, double *PHIR, double *PHII, \
           double *ZETA1R, double *ZETA1I, double *ZETA2R, double *ZETA2I, double *SUMR, double *SUMI, double *CWORKR, double *CWORKI, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zunik with init=%d\n",*INIT);
	double ac, crfni, crfnr, rfn, si, sr, sri, srr, sti, str, test, ti, tr, t2i, t2r, zni, znr;
	double con[2];
	int    i, idum, j, k, l;

	con[0] = 0.39894228040143267793994605993438186848; //1/sqrt(2pi)
	con[1] = 1.25331413731550025120788264240552262650; //sqrt(pi/2)

	if(*INIT!=0) goto IK40;
//C-----------------------------------------------------------------------
//C     INITIALIZE ALL VARIABLES
//C-----------------------------------------------------------------------
	rfn = 1.0/fnu;
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST (ZR/FNU TOO SMALL)
//C-----------------------------------------------------------------------
	test = 1000.0*D1MACH[0];
	ac = fnu*test;
	if(std::abs(zr)>ac || std::abs(zi)>ac) goto IK15;
	*ZETA1R = 2.0*std::abs(std::log(test))+fnu;
	*ZETA1I = 0.0;
	*ZETA2R = fnu;
	*ZETA2I = 0.0;
	*PHIR = 1.0;
	*PHII = 0.0;
	return;
IK15:
	tr = zr*rfn;
	ti = zi*rfn;
	sr = CONER + (tr*tr-ti*ti);
	si = CONEI + (tr*ti+ti*tr);
	zsqrt(sr, si, &srr, &sri);
	str = CONER + srr;
	sti = CONEI + sri;
	zdiv(str, sti, tr, ti, &znr, &zni);
	zlog(znr, zni, &str, &sti, &idum);
	*ZETA1R = fnu*str;
	*ZETA1I = fnu*sti;
	*ZETA2R = fnu*srr;
	*ZETA2I = fnu*sri;
	zdiv(CONER, CONEI, srr, sri, &tr, &ti);
	srr = tr*rfn;
	sri = ti*rfn;
	zsqrt(srr, sri, &(CWORKR[15]), &(CWORKI[15]));
	*PHIR = CWORKR[15]*con[ikflg-1];
	*PHII = CWORKI[15]*con[ikflg-1];
	if(ipmtr!=0) return;
	zdiv(CONER, CONEI, sr, si, &t2r, &t2i);
	CWORKR[0] = CONER;
	CWORKI[0] = CONEI;
	crfnr = CONER;
	crfni = CONEI;
	ac = 1.0;
	l = 1;
	for(k=2; k<=15; k++) { //DO 20
		sr = CZEROR;
		si = CZEROI;
		for(j=1; j<=k; j++) { //DO 10
			l = l + 1;
			str = sr*t2r - si*t2i + C[l-1];
			si = sr*t2i + si*t2r;
			sr = str;
		} //CONTINUE 10
		str = crfnr*srr - crfni*sri;
		crfni = crfnr*sri + crfni*srr;
		crfnr = str;
		CWORKR[k-1] = crfnr*sr - crfni*si;
		CWORKI[k-1] = crfnr*si + crfni*sr;
		ac = ac*rfn;
		test = std::abs(CWORKR[k-1]) + std::abs(CWORKI[k-1]);
		if(ac<tol && test<tol) goto IK30;
	} //CONTINUE 20
	k = 15;
IK30:
	*INIT = k;
IK40:
	if(ikflg==2) goto IK60;
//C-----------------------------------------------------------------------
//C     COMPUTE SUM FOR THE I FUNCTION
//C-----------------------------------------------------------------------
	sr = CZEROR;
	si = CZEROI;
	for(i=1; i<=*INIT; i++) { //DO 50
		sr = sr + CWORKR[i-1];
		si = si + CWORKI[i-1];
	} //CONTINUE 50
	*SUMR = sr;
	*SUMI = si;
	*PHIR = CWORKR[15]*con[0];
	*PHII = CWORKI[15]*con[0];
	return;
IK60:
//C-----------------------------------------------------------------------
//C     COMPUTE SUM FOR THE K FUNCTION
//C-----------------------------------------------------------------------
	sr = CZEROR;
	si = CZEROI;
	tr = CONER;
	for(i=1; i<=*INIT; i++) { //DO 70
		sr = sr + tr*CWORKR[i-1];
		si = si + tr*CWORKI[i-1];
		tr = -tr;
	} //CONTINUE 70
	*SUMR = sr;
	*SUMI = si;
	*PHIR = CWORKR[15]*con[1];
	*PHII = CWORKI[15]*con[1];
	return;
}




//use: cuchk
void zkscl(double zr, double zi, double fnu, int n, double *YR, double *YI, int *NZ, double rzr, double rzi, double ascle, double tol, double elim, int* debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zkscl\n");
	double acs, alas, as, cki, ckr, csi, csr, fn, str, s1i, s1r, s2i, s2r, zdi, zdr, celmr, elm, helim;
	double cyi[2], cyr[2];
	int    i, ic, idum, kk, nn, nw;

	*NZ = 0;
	ic = 0;
	nn = std::min(2,n);
	for(i=1; i<=nn; i++) { //DO 10
		s1r = YR[i-1];
		s1i = YI[i-1];
		cyr[i-1] = s1r;
		cyi[i-1] = s1i;
		as = zabs(s1r,s1i);
		acs = -zr + std::log(as);
		*NZ = *NZ + 1;
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
		if(acs<(-elim)) continue; //GO TO 10
		zlog(s1r, s1i, &csr, &csi, &idum);
		csr = csr - zr;
		csi = csi - zi;
		str = std::exp(csr)/tol;
		csr = str*std::cos(csi);
		csi = str*std::sin(csi);
		zuchk(csr, csi, &nw, ascle, tol, debug);
		if(nw!=0) continue; // GO TO 10
		YR[i-1] = csr;
		YI[i-1] = csi;
		ic = i;
		*NZ = *NZ - 1;
	} //CONTINUE 10
	if(n==1) return;
	if(ic>1) goto CL20;
	YR[0] = CZEROR;
	YI[0] = CZEROI;
	*NZ = 2;
CL20:
	if(n==2) return;
	if(*NZ==0) return;
	fn = fnu + 1.0;
	ckr = fn*rzr;
	cki = fn*rzi;
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	helim = 0.5*elim;
	elm = std::exp(-elim);
	celmr = elm;
	zdr = zr;
	zdi = zi;
//C
//C     FIND TWO CONSECUTIVE Y VALUES ON SCALE. SCALE RECURRENCE IF
//C     S2 GETS LARGER THAN EXP(ELIM/2)
//C
	for(i=3; i<=n; i++) { //DO 30
		kk = i;
		csr = s2r;
		csi = s2i;
		s2r = ckr*csr - cki*csi + s1r;
		s2i = cki*csr + ckr*csi + s1i;
		s1r = csr;
		s1i = csi;
		ckr = ckr + rzr;
		cki = cki + rzi;
		as = zabs(s2r,s2i);
		alas = std::log(as);
		acs = -zdr + alas;
		*NZ = *NZ + 1;
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
		if(acs<(-elim)) goto CL25;
		zlog(s2r, s2i, &csr, &csi, &idum);
		csr = csr - zdr;
		csi = csi - zdi;
		str = std::exp(csr)/tol;
		csr = str*std::cos(csi);
		csi = str*std::sin(csi);
		zuchk(csr, csi, &nw, ascle, tol, debug);
		if(nw!=0) goto CL25;
		YR[i-1] = csr;
		YI[i-1] = csi;
		*NZ = *NZ - 1;
		if(ic==kk-1) goto CL40;
		ic = kk;
		continue; //GO TO 30
CL25:
		if(alas<helim) continue; //GO TO 30
		zdr = zdr - elim;
		s1r = s1r*celmr;
		s1i = s1i*celmr;
		s2r = s2r*celmr;
		s2i = s2i*celmr;
	} //CONTINUE 30
	*NZ = n;
	if(ic==n) *NZ = n-1;
	goto CL45;
CL40:
	*NZ = kk - 2;
CL45:
	for(i=1; i<=*NZ; i++) { //DO 50
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 50
	return;
}
//use: gamln
void zmlri(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, double tol, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zmlri\n");
	double ack, ak, ap, at, az, bk, cki, ckr, cnormi, cnormr, fkap, fkk, flam, fnf, \
	       pti, ptr, p1i, p1r, p2i, p2r, raz, rho, rho2, rzi, rzr, scle, sti, str, \
	       sumi, sumr, tfnf, tst;
	int    i, iaz, idum, ifnu, inu, itime, k, kk, km, m;

	scle = D1MACH[0]/tol;
	*NZ = 0;
	az = zabs(zr,zi);
	iaz = (int)az;
	ifnu = (int)fnu;
	inu = ifnu + n - 1;
	at = (double)iaz + 1.0;
	raz = 1.0/az;
	str = zr*raz;
	sti = -zi*raz;
	ckr = str*at*raz;
	cki = sti*at*raz;
	rzr = (str+str)*raz;
	rzi = (sti+sti)*raz;
	p1r = CZEROR;
	p1i = CZEROI;
	p2r = CONER;
	p2i = CONEI;
	ack = (at+1.0)*raz;
	rho = ack + std::sqrt(ack*ack-1.0);
	rho2 = rho*rho;
	tst = (rho2+rho2)/((rho2-1.0)*(rho-1.0));
	tst = tst/tol;
//C-----------------------------------------------------------------------
//C     COMPUTE RELATIVE TRUNCATION ERROR INDEX FOR SERIES
//C-----------------------------------------------------------------------
	ak = at;
	for(i=1; i<=80; i++) { //DO 10
		ptr = p2r;
		pti = p2i;
		p2r = p1r - (ckr*ptr-cki*pti);
		p2i = p1i - (cki*ptr+ckr*pti);
		p1r = ptr;
		p1i = pti;
		ckr = ckr + rzr;
		cki = cki + rzi;
		ap = zabs(p2r,p2i);
		if(ap>tst*ak*ak) goto ML20;
		ak = ak + 1.0;
	} //CONTINUE 10
	goto ML110;
ML20:
	i = i + 1;
	k = 0;
	if(inu<iaz) goto ML40;
//C-----------------------------------------------------------------------
//C     COMPUTE RELATIVE TRUNCATION ERROR FOR RATIOS
//C-----------------------------------------------------------------------
	p1r = CZEROR;
	p1i = CZEROI;
	p2r = CONER;
	p2i = CONEI;
	at = (double)inu + 1.0;
	str = zr*raz;
	sti = -zi*raz;
	ckr = str*at*raz;
	cki = sti*at*raz;
	ack = at*raz;
	tst = std::sqrt(ack/tol);
	itime = 1;
	for(k=1; k<=80; k++) { //DO 30
		ptr = p2r;
		pti = p2i;
		p2r = p1r - (ckr*ptr-cki*pti);
		p2i = p1i - (ckr*pti+cki*ptr);
		p1r = ptr;
		p1i = pti;
		ckr = ckr + rzr;
		cki = cki + rzi;
		ap = zabs(p2r,p2i);
		if(ap<tst) continue; //GO TO 30
		if(itime==2) goto ML40;
		ack = zabs(ckr,cki);
		flam = ack + std::sqrt(ack*ack-1.0);
		fkap = ap/zabs(p1r,p1i);
		rho = std::min(flam,fkap);
		tst = tst*std::sqrt(rho/(rho*rho-1.0));
		itime = 2;
	} //CONTINUE 30
	goto ML110;
ML40:
//C-----------------------------------------------------------------------
//C     BACKWARD RECURRENCE AND SUM NORMALIZING RELATION
//C-----------------------------------------------------------------------
	k = k + 1;
	kk = std::max(i+iaz,k+inu);
	fkk = (double)kk;
	p1r = CZEROR;
	p1i = CZEROI;
//C-----------------------------------------------------------------------
//C     SCALE P2 AND SUM BY SCLE
//C-----------------------------------------------------------------------
	p2r = scle;
	p2i = CZEROI;
	fnf = fnu - (double)ifnu;
	tfnf = fnf + fnf;
	bk = dgamln(fkk+tfnf+1.0) - dgamln(fkk+1.0) - dgamln(tfnf+1.0);
	bk = std::exp(bk);
	sumr = CZEROR;
	sumi = CZEROI;
	km = kk - inu;
	for(i=1; i<=km; i++) { //DO 50
		ptr = p2r;
		pti = p2i;
		p2r = p1r + (fkk+fnf)*(rzr*ptr-rzi*pti);
		p2i = p1i + (fkk+fnf)*(rzi*ptr+rzr*pti);
		p1r = ptr;
		p1i = pti;
		ak = 1.0 - tfnf/(fkk+tfnf);
		ack = bk*ak;
		sumr = sumr + (ack+bk)*p1r;
		sumi = sumi + (ack+bk)*p1i;
		bk = ack;
		fkk = fkk - 1.0;
	} //CONTINUE 50
	YR[n-1] = p2r;
	YI[n-1] = p2i;
	if(n==1) goto ML70;
	for(i=2; i<=n; i++) { //DO 60
		ptr = p2r;
		pti = p2i;
		p2r = p1r + (fkk+fnf)*(rzr*ptr-rzi*pti);
		p2i = p1i + (fkk+fnf)*(rzi*ptr+rzr*pti);
		p1r = ptr;
		p1i = pti;
		ak = 1.0 - tfnf/(fkk+tfnf);
		ack = bk*ak;
		sumr = sumr + (ack+bk)*p1r;
		sumi = sumi + (ack+bk)*p1i;
		bk = ack;
		fkk = fkk - 1.0;
		m = n - i + 1;
		YR[m-1] = p2r;
		YI[m-1] = p2i;
	} //CONTINUE 60
ML70:
	if(ifnu<=0) goto ML90;
	for(i=1; i<=ifnu; i++) { //DO 80
		ptr = p2r;
		pti = p2i;
		p2r = p1r + (fkk+fnf)*(rzr*ptr-rzi*pti);
		p2i = p1i + (fkk+fnf)*(rzr*pti+rzi*ptr);
		p1r = ptr;
		p1i = pti;
		ak = 1.0 - tfnf/(fkk+tfnf);
		ack = bk*ak;
		sumr = sumr + (ack+bk)*p1r;
		sumi = sumi + (ack+bk)*p1i;
		bk = ack;
		fkk = fkk - 1.0;
	} //CONTINUE 80
ML90:
	ptr = zr;
	pti = zi;
	if(kode==2) ptr = CZEROR;
	zlog(rzr, rzi, &str, &sti, &idum);
	p1r = -fnf*str + ptr;
	p1i = -fnf*sti + pti;
	ap = dgamln(1.0+fnf);
	ptr = p1r - ap;
	pti = p1i;
//C-----------------------------------------------------------------------
//C     THE DIVISION CEXP(PT)/(SUM+P2) IS ALTERED TO AVOID OVERFLOW
//C     IN THE DENOMINATOR BY SQUARING LARGE QUANTITIES
//C-----------------------------------------------------------------------
	p2r = p2r + sumr;
	p2i = p2i + sumi;
	ap = zabs(p2r,p2i);
	p1r = 1.0/ap;
	zexp(ptr, pti, &str, &sti);
	ckr = str*p1r;
	cki = sti*p1r;
	ptr = p2r*p1r;
	pti = -p2i*p1r;
	zmlt(ckr, cki, ptr, pti, &cnormr, &cnormi);
	for(i=1; i<=n; i++) { //DO 100
		str = YR[i-1]*cnormr - YI[i-1]*cnormi;
		YI[i-1] = YR[i-1]*cnormi + YI[i-1]*cnormr;
		YR[i-1] = str;
	} //CONTINUE 100
	return;
ML110:
	*NZ = -2;
	return;
}
//use: cuchk,gamln
void zseri(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zseri\n");
	double aa, acz, ak, ak1i, ak1r, arm, ascle, atol, az, cki, ckr, coefi, coefr, crscr, czi, czr, dfnu, \
	       fnup, hzi, hzr, raz, rs, rtr1, rzi, rzr, s, ss, sti, str, s1i, s1r, s2i, s2r;
	double wi[2], wr[2];
	int    i, ib, idum, iflag, il, k, l, m, nn, nw;

	//initialize, so the compiler is happy
	nn = 0;
	//end of extra initialization

	*NZ = 0;
	az = zabs(zr,zi);
	if(az==0.0) goto SE160;
	arm = 1000.0*D1MACH[0];
	rtr1 = std::sqrt(arm);
	crscr = 1.0;
	iflag = 0;
	if(az<arm) goto SE150;
	hzr = 0.5*zr;
	hzi = 0.5*zi;
	czr = CZEROR;
	czi = CZEROI;
	if(az<=rtr1) goto SE10;
	zmlt(hzr, hzi, hzr, hzi, &czr, &czi);
SE10:
	acz = zabs(czr,czi);
	nn = n;
	zlog(hzr, hzi, &ckr, &cki, &idum);
SE20:
	dfnu = fnu + (double)(nn-1);
	fnup = dfnu + 1.0;
//C-----------------------------------------------------------------------
//C     UNDERFLOW TEST
//C-----------------------------------------------------------------------
	ak1r = ckr*dfnu;
	ak1i = cki*dfnu;
	ak = dgamln(fnup);
	ak1r = ak1r - ak;
	if(kode==2) ak1r = ak1r - zr;
	if(ak1r>(-elim)) goto SE40;
SE30:
	*NZ = *NZ + 1;
	YR[nn-1] = CZEROR;
	YI[nn-1] = CZEROI;
	if(acz>dfnu) goto SE190;
	nn = nn - 1;
	if(nn==0) return;
	goto SE20;
SE40:
	if(ak1r>(-alim)) goto SE50;
	iflag = 1;
	ss = 1.0/tol;
	crscr = tol;
	ascle = arm*ss;
SE50:
	aa = std::exp(ak1r);
	if(iflag==1) aa = aa*ss;
	coefr = aa*std::cos(ak1i);
	coefi = aa*std::sin(ak1i);
	atol = tol*acz/fnup;
	il = std::min(2,nn);
	for(i=1; i<=il; i++) { //DO 90
		dfnu = fnu + (double)(nn-i);
		fnup = dfnu + 1.0;
		s1r = CONER;
		s1i = CONEI;
		if(acz<tol*fnup) goto SE70;
		ak1r = CONER;
		ak1i = CONEI;
		ak = fnup + 2.0;
		s = fnup;
		aa = 2.0;
SE60:
		rs = 1.0/s;
		str = ak1r*czr - ak1i*czi;
		sti = ak1r*czi + ak1i*czr;
		ak1r = str*rs;
		ak1i = sti*rs;
		s1r = s1r + ak1r;
		s1i = s1i + ak1i;
		s = s + ak;
		ak = ak + 2.0;
		aa = aa*acz*rs;
		if(aa>atol) goto SE60;
SE70:
		s2r = s1r*coefr - s1i*coefi;
		s2i = s1r*coefi + s1i*coefr;
		wr[i-1] = s2r;
		wi[i-1] = s2i;
		if(iflag==0) goto SE80;
		zuchk(s2r, s2i, &nw, ascle, tol, debug);
		if(nw!=0) goto SE30;
SE80:
		m = nn - i + 1;
		YR[m-1] = s2r*crscr;
		YI[m-1] = s2i*crscr;
		if(i==il) continue; //GO TO 90
		zdiv(coefr, coefi, hzr, hzi, &str, &sti);
		coefr = str*dfnu;
		coefi = sti*dfnu;
	} //CONTINUE 90
	if(nn<=2) return;
	k = nn - 2;
	ak = (double)k;
	raz = 1.0/az;
	str = zr*raz;
	sti = -zi*raz;
	rzr = (str+str)*raz;
	rzi = (sti+sti)*raz;
	if(iflag==1) goto SE120;
	ib = 3;
SE100:
	for(i=ib; i<=nn; i++) { //DO 110
		YR[k-1] = (ak+fnu)*(rzr*YR[k]-rzi*YI[k]) + YR[k+1];
		YI[k-1] = (ak+fnu)*(rzr*YI[k]+rzi*YR[k]) + YI[k+1];
		ak = ak - 1.0;
		k = k - 1;
	} //CONTINUE 110
	return;
//C-----------------------------------------------------------------------
//C     RECUR BACKWARD WITH SCALED VALUES
//C-----------------------------------------------------------------------
SE120:
//C-----------------------------------------------------------------------
//C     EXP(-ALIM)=EXP(-ELIM)/TOL=APPROX. ONE PRECISION ABOVE THE
//C     UNDERFLOW LIMIT = ASCLE = D1MACH(1)*SS*1.0D+3
//C-----------------------------------------------------------------------
	s1r = wr[0];
	s1i = wi[0];
	s2r = wr[1];
	s2i = wi[1];
	for(l=3; l<=nn; l++) { //DO 130
		ckr = s2r;
		cki = s2i;
		s2r = s1r + (ak+fnu)*(rzr*ckr-rzi*cki);
		s2i = s1i + (ak+fnu)*(rzr*cki+rzi*ckr);
		s1r = ckr;
		s1i = cki;
		ckr = s2r*crscr;
		cki = s2i*crscr;
		YR[k-1] = ckr;
		YI[k-1] = cki;
		ak = ak - 1.0;
		k = k - 1;
		if(zabs(ckr,cki)>ascle) goto SE140;
	} //CONTINUE 130
	return;
SE140:
	ib = l + 1;
	if(ib>nn) return;
	goto SE100;
SE150:
	*NZ = n;
	if(fnu==0.0) *NZ = *NZ - 1;
SE160:
	YR[0] = CZEROR;
	YI[0] = CZEROI;
	if(fnu!=0.0) goto SE170;
	YR[0] = CONER;
	YI[0] = CONEI;
SE170:
	if(n==1) return;
	for(i=2; i<=nn; i++) { //DO 180
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 180
	return;
//C-----------------------------------------------------------------------
//C     RETURN WITH NZ.LT.0 IF CABS(Z*Z/4).GT.FNU+N-NZ-1 COMPLETE
//C     THE CALCULATION IN CBINU WITH N=N-IABS(NZ)
//C-----------------------------------------------------------------------
SE190:
	*NZ = -*NZ;
	return;
}
//use: cuchk, cunhj, cunik
void zuoik(double zr, double zi, double fnu, int kode, int ikflg, int n, double *YR, double *YI, int *NUF, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zuoik\n");
	double aarg, aphi, argi, argr, ascle, asumi, asumr, ax, ay, bsumi, bsumr, czi, czr, \
	       fnn, gnn, gnu, phii, phir, rcz, sti, str, sumi, sumr, zbi, zbr, \
	       zeta1i, zeta1r, zeta2i, zeta2r, zni, znr, zri, zrr;
	double cworki[16], cworkr[16];
	int    i, idum, iform, init, nn, nw;

	*NUF = 0;
	nn = n;
	zrr = zr;
	zri = zi;
	if(zr>=0.0) goto UO10;
	zrr = -zr;
	zri = -zi;
UO10:
	zbr = zrr;
	zbi = zri;
	ax = std::abs(zr)*RT3; //1.7321;
	ay = std::abs(zi);
	iform = 1;
	if(ay>ax) iform = 2;
	gnu = std::max(fnu,1.0);
	if(ikflg==1) goto UO20;
	fnn = (double)nn;
	gnn = fnu + fnn - 1.0;
	gnu = std::max(gnn,fnn);
UO20:
//C-----------------------------------------------------------------------
//C     ONLY THE MAGNITUDE OF ARG AND PHI ARE NEEDED ALONG WITH THE
//C     REAL PARTS OF ZETA1, ZETA2 AND ZB. NO ATTEMPT IS MADE TO GET
//C     THE SIGN OF THE IMAGINARY PART CORRECT.
//C-----------------------------------------------------------------------
	if(iform==2) goto UO30;
	init = 0;
	zunik(zrr, zri, gnu, ikflg, 1, tol, &init, &phir, &phii, \
	      &zeta1r, &zeta1i, &zeta2r, &zeta2i, &sumr, &sumi, cworkr, cworki, debug);
	czr = -zeta1r + zeta2r;
	czi = -zeta1i + zeta2i;
	goto UO50;
UO30:
	znr = zri;
	zni = -zrr;
	if(zi>0.0) goto UO40;
	znr = -znr;
UO40:
	zunhj(znr, zni, gnu, 1, tol, &phir, &phii, &argr, &argi, &zeta1r, &zeta1i, \
	      &zeta2r, &zeta2i, &asumr, &asumi, &bsumr, &bsumi, debug);
	czr = -zeta1r + zeta2r;
	czi = -zeta1i + zeta2i;
	aarg = zabs(argr,argi);
UO50:
	if(kode==1) goto UO60;
	czr = czr - zbr;
	czi = czi - zbi;
UO60:
	if(ikflg==1) goto UO70;
	czr = -czr;
	czi = -czi;
UO70:
	aphi = zabs(phir,phii);
	rcz = czr;
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST
//C-----------------------------------------------------------------------
	if(rcz>elim) goto UO210;
	if(rcz<alim) goto UO80;
	rcz = rcz + std::log(aphi);
	if(iform==2) rcz = rcz - 0.25*std::log(aarg) - AIC;
	if(rcz>elim) goto UO210;
	goto UO130;
UO80:
//C-----------------------------------------------------------------------
//C     UNDERFLOW TEST
//C-----------------------------------------------------------------------
	if(rcz<(-elim)) goto UO90;
	if(rcz>(-alim)) goto UO130;
	rcz = rcz + std::log(aphi);
	if(iform==2) rcz = rcz - 0.25*std::log(aarg) - AIC;
	if(rcz>(-elim)) goto UO110;
UO90:
	for(i=1; i<=nn; i++) { //DO 100
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 100
	*NUF = nn;
	return;
UO110:
	ascle = 1000.0*D1MACH[0]/tol;
	zlog(phir, phii, &str, &sti, &idum);
	czr = czr + str;
	czi = czi + sti;
	if(iform==1) goto UO120;
	zlog(argr, argi, &str, &sti, &idum);
	czr = czr - 0.25*str - AIC;
	czi = czi - 0.25*sti;
UO120:
	ax = std::exp(rcz)/tol;
	ay = czi;
	czr = ax*std::cos(ay);
	czi = ax*std::sin(ay);
	zuchk(czr, czi, &nw, ascle, tol, debug);
	if(nw!=0) goto UO90;
UO130:
	if(ikflg==2) return;
	if(n==1) return;
//C-----------------------------------------------------------------------
//C     SET UNDERFLOWS ON I SEQUENCE
//C-----------------------------------------------------------------------
UO140:
	gnu = fnu + (double)(nn-1);
	if(iform==2) goto UO150;
	init = 0;
	zunik(zrr, zri, gnu, ikflg, 1, tol, &init, &phir, &phii, \
	      &zeta1r, &zeta1i, &zeta2r, &zeta2i, &sumr, &sumi, cworkr, cworki, debug);
	czr = -zeta1r + zeta2r;
	czi = -zeta1i + zeta2i;
	goto UO160;
UO150:
	zunhj(znr, zni, gnu, 1, tol, &phir, &phii, &argr, &argi, \
	      &zeta1r, &zeta1i, &zeta2r, &zeta2i, &asumr, &asumi, &bsumr, &bsumi, debug);
	czr = -zeta1r + zeta2r;
	czi = -zeta1i + zeta2i;
	aarg = zabs(argr,argi);
UO160:
	if(kode==1) goto UO170;
	czr = czr - zbr;
	czi = czi - zbi;
UO170:
	aphi = zabs(phir,phii);
	rcz = czr;
	if(rcz<(-elim)) goto UO180;
	if(rcz>(-alim)) return;
	rcz = rcz + std::log(aphi);
	if(iform==2) rcz = rcz - 0.25*std::log(aarg) - AIC;
	if(rcz>(-elim)) goto UO190;
UO180:
	YR[nn-1] = CZEROR;
	YI[nn-1] = CZEROI;
	nn = nn - 1;
	*NUF = *NUF + 1;
	if(nn==0) return;
	goto UO140;
UO190:
	ascle = 1000.0*D1MACH[0]/tol;
	zlog(phir, phii, &str, &sti, &idum);
	czr = czr + str;
	czi = czi + sti;
	if(iform==1) goto UO200;
	zlog(argr, argi, &str, &sti, &idum);
	czr = czr - 0.25*str - AIC;
	czi = czi - 0.25*sti;
UO200:
	ax = std::exp(rcz)/tol;
	ay = czi;
	czr = ax*std::cos(ay);
	czi = ax*std::sin(ay);
	zuchk(czr, czi, &nw, ascle, tol, debug);
	if(nw!=0) goto UO180;
	return;
UO210:
	*NUF = -1;
	return;
}




//*****************************************************
//**** Bessel K function                           ****
//**** modified Bessel function of the second kind ****
//*****************************************************

static const double CC[8] = {
		5.77215664901532861E-01, -4.20026350340952355E-02, -4.21977345555443367E-02, 7.21894324666309954E-03, -2.15241674114950973E-04,
		-2.01348547807882387E-05, 1.13302723198169588E-06, 6.11609510448141582E-09
};
//use: ckscl, cshch, cuchk, gamln
void zbknu(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbknu\n");
	double aa, alas, ak, as, ascle, a1, a2, bb, bk, caz, cbi, cbr, cchi, cchr, celmr, cki, ckr, coefi, \
	       coefr, crscr, csclr, cshi, cshr, csi, csr, czi, czr, dnu, dnu2, elm, etest, fc, fhs, fi, fr, \
	       fk, fks, fmui, fmur, g1, g2, helim, pi, pr, pti, ptr, p1i, p1r, p2i, p2m, p2r, qi, qr, rak, \
	       rcaz, rzi, rzr, r1, s, smui, smur, sti, str, s1i, s1r, s2i, s2r, tm, t1, t2, zdi, zdr;
	double bry[3], csrr[3], cssr[3], cyi[2], cyr[2];
	int    i, ic, idum, iflag, inu, inub, j, k, kflag, kk, koded, nw;

	//initialize, so the compiler is happy
	r1 = 0.0;
	ckr = 0.0;
	cki = 0.0;
	//end of extra initialization

	caz = zabs(zr,zi);
	csclr = 1.0/tol;
	crscr = tol;
	cssr[0] = csclr;
	cssr[1] = CONER;
	cssr[2] = crscr;
	csrr[0] = crscr;
	csrr[1] = CONER;
	csrr[2] = csclr;
	bry[0] = 1000.0*D1MACH[0]/tol;
	bry[1] = 1.0/bry[0];
	bry[2] = D1MACH[1];
	*NZ = 0;
	iflag = 0;
	koded = kode;
	rcaz = 1.0/caz;
	str = zr*rcaz;
	sti = -zi*rcaz;
	rzr = (str+str)*rcaz;
	rzi = (sti+sti)*rcaz;
	inu = (int)(fnu+0.5);
	dnu = fnu - (double)inu;
	if(std::abs(dnu)==0.5) goto BK110;
	dnu2 = 0.0;
	if(std::abs(dnu)>tol) dnu2 = dnu*dnu;
	if(caz>r1) goto BK110;
//C-----------------------------------------------------------------------
//C     SERIES FOR CABS(Z).LE.R1
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZKBNU: series for |z|<=r1\n");
	fc = 1.0;
	zlog(rzr, rzi, &smur, &smui, &idum);
	fmur = smur*dnu;
	fmui = smui*dnu;
	zshch(fmur, fmui, &cshr, &cshi, &cchr, &cchi);
	if(dnu==0.0) goto BK10;
	fc = dnu*_PI_;
	fc = fc/std::sin(fc);
	smur = cshr/dnu;
	smui = cshi/dnu;
BK10:
	a2 = 1.0 + dnu;
//C-----------------------------------------------------------------------
//C     GAM(1-Z)*GAM(1+Z)=PI*Z/SIN(PI*Z), T1=1/GAM(1-DNU), T2=1/GAM(1+DNU)
//C-----------------------------------------------------------------------
	t2 = std::exp(-dgamln(a2));
	t1 = 1.0/(t2*fc);
	if(std::abs(dnu)>0.1) goto BK40;
//C-----------------------------------------------------------------------
//C     SERIES FOR F0 TO RESOLVE INDETERMINACY FOR SMALL ABS(DNU)
//C-----------------------------------------------------------------------
	ak = 1.0;
	s = CC[0];
	for(k=2; k<=8; k++) { //DO 20
		ak = ak*dnu2;
		tm = CC[k-1]*ak;
		s = s + tm;
		if(std::abs(tm)<tol) goto BK30;
	} //CONTINUE 20
BK30:
	g1 = -s;
	goto BK50;
BK40:
	g1 = (t1-t2)/(dnu+dnu);
BK50:
	g2 = (t1+t2)*0.5;
	fr = fc*(cchr*g1+smur*g2);
	fi = fc*(cchi*g1+smui*g2);
	zexp(fmur, fmui, &str, &sti);
	pr = 0.5*str/t2;
	pi = 0.5*sti/t2;
	zdiv(0.5, 0.0, str, sti, &ptr, &pti);
	qr = ptr/t1;
	qi = pti/t1;
	s1r = fr;
	s1i = fi;
	s2r = pr;
	s2i = pi;
	ak = 1.0;
	a1 = 1.0;
	ckr = CONER;
	cki = CONEI;
	bk = 1.0 - dnu2;
	if(inu>0 || n>1) goto BK80;
//C-----------------------------------------------------------------------
//C     GENERATE K(FNU,Z), 0.0D0 .LE. FNU .LT. 0.5D0 AND N=1
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU: generate K(dv,z) for 0.0<=v<0.5 and n=1\n");
	if(caz<tol) goto BK70;
	zmlt(zr, zi, zr, zi, &czr, &czi);
	czr = 0.25*czr;
	czi = 0.25*czi;
	t1 = 0.25*caz*caz;
BK60:
	fr = (fr*ak+pr+qr)/bk;
	fi = (fi*ak+pi+qi)/bk;
	str = 1.0/(ak-dnu);
	pr = pr*str;
	pi = pi*str;
	str = 1.0/(ak+dnu);
	qr = qr*str;
	qi = qi*str;
	str = ckr*czr - cki*czi;
	rak = 1.0/ak;
	cki = (ckr*czi+cki*czr)*rak;
	ckr = str*rak;
	s1r = ckr*fr - cki*fi + s1r;
	s1i = ckr*fi + cki*fr + s1i;
	a1 = a1*t1*rak;
	bk = bk + ak + ak + 1.0;
	ak = ak + 1.0;
	if(a1>tol) goto BK60;
BK70:
	YR[0] = s1r;
	YI[0] = s1i;
	if(koded==1) return;
	zexp(zr, zi, &str, &sti);
	zmlt(s1r, s1i, str, sti, &(YR[0]), &(YI[0]));
	return;
//C-----------------------------------------------------------------------
//C     GENERATE K(DNU,Z) AND K(DNU+1,Z) FOR FORWARD RECURRENCE
//C-----------------------------------------------------------------------
BK80:
	if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU: generate K(dv,z) & K(1+dv,z) for forward recurrence\n");
	if(caz<tol) goto BK100;
	zmlt(zr, zi, zr, zi, &czr, &czi);
	czr = 0.25*czr;
	czi = 0.25*czi;
	t1 = 0.25*caz*caz;
BK90:
	fr = (fr*ak+pr+qr)/bk;
	fi = (fi*ak+pi+qi)/bk;
	str = 1.0/(ak-dnu);
	pr = pr*str;
	pi = pi*str;
	str = 1.0/(ak+dnu);
	qr = qr*str;
	qi = qi*str;
	str = ckr*czr - cki*czi;
	rak = 1.0/ak;
	cki = (ckr*czi+cki*czr)*rak;
	ckr = str*rak;
	s1r = ckr*fr - cki*fi + s1r;
	s1i = ckr*fi + cki*fr + s1i;
	str = pr - fr*ak;
	sti = pi - fi*ak;
	s2r = ckr*str - cki*sti + s2r;
	s2i = ckr*sti + cki*str + s2i;
	a1 = a1*t1*rak;
	bk = bk + ak + ak + 1.0;
	ak = ak + 1.0;
	if(a1>tol) goto BK90;
BK100:
	kflag = 2;
	a1 = fnu + 1.0;
	ak = a1*std::abs(smur);
	if(ak>alim) kflag = 3;
	str = cssr[kflag-1];
	p2r = s2r*str;
	p2i = s2i*str;
	zmlt(p2r, p2i, rzr, rzi, &s2r, &s2i);
	s1r = s1r*str;
	s1i = s1i*str;
	if(koded==1) goto BK210;
	zexp(zr, zi, &fr, &fi);
	zmlt(s1r, s1i, fr, fi, &s1r, &s1i);
	zmlt(s2r, s2i, fr, fi, &s2r, &s2i);
	goto BK210;
//C-----------------------------------------------------------------------
//C     IFLAG=0 MEANS NO UNDERFLOW OCCURRED
//C     IFLAG=1 MEANS AN UNDERFLOW OCCURRED- COMPUTATION PROCEEDS WITH
//C     KODED=2 AND A TEST FOR ON SCALE VALUES IS MADE DURING FORWARD
//C     RECURSION
//C-----------------------------------------------------------------------
BK110:
	zsqrt(zr, zi, &str, &sti);
	zdiv(RTHPI, CZEROI, str, sti, &coefr, &coefi);
	kflag = 2;
	if(koded==2) goto BK120;
	if(zr>alim) goto BK290;
//C     BLANK LINE
	str = std::exp(-zr)*cssr[kflag-1];
	sti = -str*std::sin(zi);
	str = str*std::cos(zi);
	zmlt(coefr, coefi, str, sti, &coefr, &coefi);
BK120:
	if(std::abs(dnu)==0.5) goto BK300;
//C-----------------------------------------------------------------------
//C     MILLER ALGORITHM FOR CABS(Z).GT.R1
//C-----------------------------------------------------------------------
	ak = std::cos(_PI_*dnu);
	ak = std::abs(ak);
	if(ak==CZEROR) goto BK300;
	fhs = std::abs(0.25-dnu2);
	if(fhs==CZEROR) goto BK300;
//C-----------------------------------------------------------------------
//C     COMPUTE R2=F(E). IF CABS(Z).GE.R2, USE FORWARD RECURRENCE TO
//C     DETERMINE THE BACKWARD INDEX K. R2=F(E) IS A STRAIGHT LINE ON
//C     12.LE.E.LE.60. E IS COMPUTED FROM 2**(-E)=B**(1-I1MACH(14))=
//C     TOL WHERE B IS THE BASE OF THE ARITHMETIC.
//C-----------------------------------------------------------------------
	t1 = (double)(I1MACH[13]-1);
	t1 = t1*D1MACH[4]*3.3219280948873626; //const=log(10)/log(2)
	t1 = std::max(t1,12.0);
	t1 = std::min(t1,60.0);
	t2 = 2.0*t1/3.0 - 6.0;
	if(zr!=0.0) goto BK130;
	t1 = HPI;
	goto BK140;
BK130:
	t1 = std::atan(zi/zr);
	t1 = std::abs(t1);
BK140:
	if(t2>caz) goto BK170;
//C-----------------------------------------------------------------------
//C     FORWARD RECURRENCE LOOP WHEN CABS(Z).GE.R2
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU: forward recurrence for |z|>=r2\n");
	etest = ak/(_PI_*caz*tol);
	fk = CONER;
	if(etest<CONER) goto BK180;
	fks = CTWOR;
	ckr = caz + caz + CTWOR;
	p1r = CZEROR;
	p2r = CONER;
	for(i=1; i<=30; i++) { //DO 150; //KMAX=30
		ak = fhs/fks;
		cbr = ckr/(fk+CONER);
		ptr = p2r;
		p2r = cbr*p2r - p1r*ak;
		p1r = ptr;
		ckr = ckr + CTWOR;
		fks = fks + fk + fk + CTWOR;
		fhs = fhs + fk + fk;
		fk = fk + CONER;
		str = std::abs(p2r)*fk;
		//if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU conv test: etest<str?\n    I    =%d\n    etest=%16.8e\n    str  =%16.8e\n", I, ETEST, STR);
		if(etest<str) goto BK160;
	} //CONTINUE 150
	if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU: forward recurrence did not converge.\n");
	goto BK310;
BK160:
	fk = fk + SPI*t1*std::sqrt(t2/caz);
	fhs = std::abs(0.25-dnu2);
	goto BK180;
BK170:
//C-----------------------------------------------------------------------
//C     COMPUTE BACKWARD INDEX K FOR CABS(Z).LT.R2
//C-----------------------------------------------------------------------
	a2 = std::sqrt(caz);
	ak = FPI*ak/(tol*std::sqrt(a2));
	aa = 3.0*t1/(1.0+caz);
	bb = 14.7*t1/(28.0+caz);
	ak = (std::log(ak)+caz*std::cos(aa)/(1.0+0.008*caz))/std::cos(bb);
	fk = 0.12125*ak*ak/caz + 1.5;
BK180:
//C-----------------------------------------------------------------------
//C     BACKWARD RECURRENCE LOOP FOR MILLER ALGORITHM
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU: backward recurrence for Miller algorithm\n");
	k = (int)fk;
	fk = (double)k;
	fks = fk*fk;
	p1r = CZEROR;
	p1i = CZEROI;
	p2r = tol;
	p2i = CZEROI;
	csr = p2r;
	csi = p2i;
	for(i=1; i<=k; i++) { //DO 190
		a1 = fks - fk;
		ak = (fks+fk)/(a1+fhs);
		rak = 2.0/(fk+CONER);
		cbr = (fk+zr)*rak;
		cbi = zi*rak;
		ptr = p2r;
		pti = p2i;
		p2r = (ptr*cbr-pti*cbi-p1r)*ak;
		p2i = (pti*cbr+ptr*cbi-p1i)*ak;
		p1r = ptr;
		p1i = pti;
		csr = csr + p2r;
		csi = csi + p2i;
		fks = a1 - fk + CONER;
		fk = fk - CONER;
	} //CONTINUE 190
//C-----------------------------------------------------------------------
//C     COMPUTE (P2/CS)=(P2/CABS(CS))*(CONJG(CS)/CABS(CS)) FOR BETTER
//C     SCALING
//C-----------------------------------------------------------------------
	tm = zabs(csr,csi);
	ptr = 1.0/tm;
	s1r = p2r*ptr;
	s1i = p2i*ptr;
	csr = csr*ptr;
	csi = -csi*ptr;
	zmlt(coefr, coefi, s1r, s1i, &str, &sti);
	zmlt(str, sti, csr, csi, &s1r, &s1i);
	if(inu>0 || n>1) goto BK200;
	zdr = zr;
	zdi = zi;
	if(iflag==1) goto BK270;
	goto BK240;
BK200:
//C-----------------------------------------------------------------------
//C     COMPUTE P1/P2=(P1/CABS(P2)*CONJG(P2)/CABS(P2) FOR SCALING
//C-----------------------------------------------------------------------
	tm = zabs(p2r,p2i);
	ptr = 1.0/tm;
	p1r = p1r*ptr;
	p1i = p1i*ptr;
	p2r = p2r*ptr;
	p2i = -p2i*ptr;
	zmlt(p1r, p1i, p2r, p2i, &ptr, &pti);
	str = dnu + 0.5 - ptr;
	sti = -pti;
	zdiv(str, sti, zr, zi, &str, &sti);
	str = str + 1.0;
	zmlt(str, sti, s1r, s1i, &s2r, &s2i);
//C-----------------------------------------------------------------------
//C     FORWARD RECURSION ON THE THREE TERM RECURSION WITH RELATION WITH
//C     SCALING NEAR EXPONENT EXTREMES ON KFLAG=1 OR KFLAG=3
//C-----------------------------------------------------------------------
BK210:
	if(*debug) PySys_WriteStdout("[DEBUG] ZBKNU: forward recurrence on 3-term recursion with kflag=%d\n",kflag);
	str = dnu + 1.0;
	ckr = str*rzr;
	cki = str*rzi;
	if(n==1) inu = inu - 1;
	if(inu>0) goto BK220;
	if(n>1) goto BK215;
	s1r = s2r;
	s1i = s2i;
BK215:
	zdr = zr;
	zdi = zi;
	if(iflag==1) goto BK270;
	goto BK240;
BK220:
	inub = 1;
	if(iflag==1) goto BK261;
BK225:
	p1r = csrr[kflag-1];
	ascle = bry[kflag-1];
	for(i=inub; i<=inu; i++) { //DO 230
		str = s2r;
		sti = s2i;
		s2r = ckr*str - cki*sti + s1r;
		s2i = ckr*sti + cki*str + s1i;
		s1r = str;
		s1i = sti;
		ckr = ckr + rzr;
		cki = cki + rzi;
		if(kflag>=3) continue; // GO TO 230
		p2r = s2r*p1r;
		p2i = s2i*p1r;
		str = std::abs(p2r);
		sti = std::abs(p2i);
		p2m = std::max(str,sti);
		if(p2m<=ascle) continue; //GO TO 230
		kflag = kflag + 1;
		ascle = bry[kflag-1];
		s1r = s1r*p1r;
		s1i = s1i*p1r;
		s2r = p2r;
		s2i = p2i;
		str = cssr[kflag-1];
		s1r = s1r*str;
		s1i = s1i*str;
		s2r = s2r*str;
		s2i = s2i*str;
		p1r = csrr[kflag-1];
	} //CONTINUE 230
	if(n!=1) goto BK240;
	s1r = s2r;
	s1i = s2i;
BK240:
	str = csrr[kflag-1];
	YR[0] = s1r*str;
	YI[0] = s1i*str;
	if(n==1) return;
	YR[1] = s2r*str;
	YI[1] = s2i*str;
	if(n==2) return;
	kk = 2;
BK250:
	kk = kk + 1;
	if(kk>n) return;
	p1r = csrr[kflag-1];
	ascle = bry[kflag-1];
	for(i=kk; i<=n; i++) { //DO 260
		p2r = s2r;
		p2i = s2i;
		s2r = ckr*p2r - cki*p2i + s1r;
		s2i = cki*p2r + ckr*p2i + s1i;
		s1r = p2r;
		s1i = p2i;
		ckr = ckr + rzr;
		cki = cki + rzi;
		p2r = s2r*p1r;
		p2i = s2i*p1r;
		YR[i-1] = p2r;
		YI[i-1] = p2i;
		if(kflag>=3) continue; // GO TO 260
		str = std::abs(p2r);
		sti = std::abs(p2i);
		p2m = std::max(str,sti);
		if(p2m<=ascle) continue; // GO TO 260
		kflag = kflag + 1;
		ascle = bry[kflag-1];
		s1r = s1r*p1r;
		s1i = s1i*p1r;
		s2r = p2r;
		s2i = p2i;
		str = cssr[kflag-1];
		s1r = s1r*str;
		s1i = s1i*str;
		s2r = s2r*str;
		s2i = s2i*str;
		p1r = csrr[kflag-1];
	} //CONTINUE 260
	return;
//C-----------------------------------------------------------------------
//C     IFLAG=1 CASES, FORWARD RECURRENCE ON SCALED VALUES ON UNDERFLOW
//C-----------------------------------------------------------------------
BK261:
	helim = 0.5*elim;
	elm = std::exp(-elim);
	celmr = elm;
	ascle = bry[0];
	zdr = zr;
	zdi = zi;
	ic = -1;
	j = 2;
	for(i=1; i<=inu; i++) { //DO 262
		str = s2r;
		sti = s2i;
		s2r = str*ckr-sti*cki+s1r;
		s2i = sti*ckr+str*cki+s1i;
		s1r = str;
		s1i = sti;
		ckr = ckr+rzr;
		cki = cki+rzi;
		as = zabs(s2r,s2i);
		alas = std::log(as);
		p2r = -zdr+alas;
		if(p2r<(-elim)) goto BK263;
		zlog(s2r,s2i,&str,&sti,&idum);
		p2r = -zdr+str;
		p2i = -zdi+sti;
		p2m = std::exp(p2r)/tol;
		p1r = p2m*std::cos(p2i);
		p1i = p2m*std::sin(p2i);
		zuchk(p1r,p1i,&nw,ascle,tol,debug);
		if(nw!=0) goto BK263;
		j = 3 - j;
		cyr[j-1] = p1r;
		cyi[j-1] = p1i;
		if(ic==(i-1)) goto BK264;
		ic = i;
		continue; // GO TO 262
BK263:
		if(alas<helim) continue; // GO TO 262
		zdr = zdr-elim;
		s1r = s1r*celmr;
		s1i = s1i*celmr;
		s2r = s2r*celmr;
		s2i = s2i*celmr;
	} //CONTINUE 262
	if(n!=1) goto BK270;
	s1r = s2r;
	s1i = s2i;
	goto BK270;
BK264:
	kflag = 1;
	inub = i+1;
	s2r = cyr[j-1];
	s2i = cyi[j-1];
	j = 3 - j;
	s1r = cyr[j-1];
	s1i = cyi[j-1];
	if(inub<=inu) goto BK225;
	if(n!=1) goto BK240;
	s1r = s2r;
	s1i = s2i;
	goto BK240;
BK270:
	YR[0] = s1r;
	YI[0] = s1i;
	if(n==1) goto BK280;
	YR[1] = s2r;
	YI[1] = s2i;
BK280:
	ascle = bry[0];
	zkscl(zdr,zdi,fnu,n,YR,YI,NZ,rzr,rzi,ascle,tol,elim,debug);
	inu = n - *NZ;
	if(inu<=0) return;
	kk = *NZ + 1;
	s1r = YR[kk-1];
	s1i = YI[kk-1];
	YR[kk-1] = s1r*csrr[0];
	YI[kk-1] = s1i*csrr[0];
	if(inu==1) return;
	kk = *NZ + 2;
	s2r = YR[kk-1];
	s2i = YI[kk-1];
	YR[kk-1] = s2r*csrr[0];
	YI[kk-1] = s2i*csrr[0];
	if(inu==2) return;
	t2 = fnu + (double)(kk-1);
	ckr = t2*rzr;
	cki = t2*rzi;
	kflag = 1;
	goto BK250;
BK290:
//C-----------------------------------------------------------------------
//C     SCALE BY DEXP(Z), IFLAG = 1 CASES
//C-----------------------------------------------------------------------
	koded = 2;
	iflag = 1;
	kflag = 2;
	goto BK120;
//C-----------------------------------------------------------------------
//C     FNU=HALF ODD INTEGER CASE, DNU=-0.5
//C-----------------------------------------------------------------------
BK300:
	s1r = coefr;
	s1i = coefi;
	s2r = coefr;
	s2i = coefi;
	goto BK210;
//C
//C
BK310:
	*NZ = -2;
	return;
}
//use: cbknu, crati
void zwrsk(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, double *CWR, double *CWI, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zwrsk\n");
	double act, acw, ascle, cinui, cinur, csclr, cti, ctr, c1i, c1r, c2i, c2r, pti, ptr, ract, sti, str;
	int    i, nw;

//C-----------------------------------------------------------------------
//C     I(FNU+I-1,Z) BY BACKWARD RECURRENCE FOR RATIOS
//C     Y(I)=I(FNU+I,Z)/I(FNU+I-1,Z) FROM CRATI NORMALIZED BY THE
//C     WRONSKIAN WITH K(FNU,Z) AND K(FNU+1,Z) FROM CBKNU.
//C-----------------------------------------------------------------------
	*NZ = 0;
	zbknu(zr, zi, fnu, kode, 2, CWR, CWI, &nw, tol, elim, alim, debug);
	if(nw!=0) goto WR50;
	zrati(zr, zi, fnu, n, YR, YI, tol, debug);
//C-----------------------------------------------------------------------
//C     RECUR FORWARD ON I(FNU+1,Z) = R(FNU,Z)*I(FNU,Z),
//C     R(FNU+J-1,Z)=Y(J),  J=1,...,N
//C-----------------------------------------------------------------------
	cinur = 1.0;
	cinui = 0.0;
	if(kode==1) goto WR10;
	cinur = std::cos(zi);
	cinui = std::sin(zi);
WR10:
//C-----------------------------------------------------------------------
//C     ON LOW EXPONENT MACHINES THE K FUNCTIONS CAN BE CLOSE TO BOTH
//C     THE UNDER AND OVERFLOW LIMITS AND THE NORMALIZATION MUST BE
//C     SCALED TO PREVENT OVER OR UNDERFLOW. CUOIK HAS DETERMINED THAT
//C     THE RESULT IS ON SCALE.
//C-----------------------------------------------------------------------
	acw = zabs(CWR[1],CWI[1]);
	ascle = 1000.0*D1MACH[0]/tol;
	csclr = 1.0;
	if(acw>ascle) goto WR20;
	csclr = 1.0/tol;
	goto WR30;
WR20:
	ascle = 1.0/ascle;
	if(acw<ascle) goto WR30;
	csclr = tol;
WR30:
	c1r = CWR[0]*csclr;
	c1i = CWI[0]*csclr;
	c2r = CWR[1]*csclr;
	c2i = CWI[1]*csclr;
	str = YR[0];
	sti = YI[0];
//C-----------------------------------------------------------------------
//C     CINU=CINU*(CONJG(CT)/CABS(CT))*(1.0D0/CABS(CT) PREVENTS
//C     UNDER- OR OVERFLOW PREMATURELY BY SQUARING CABS(CT)
//C-----------------------------------------------------------------------
	ptr = str*c1r - sti*c1i;
	pti = str*c1i + sti*c1r;
	ptr = ptr + c2r;
	pti = pti + c2i;
	ctr = zr*ptr - zi*pti;
	cti = zr*pti + zi*ptr;
	act = zabs(ctr,cti);
	ract = 1.0/act;
	ctr = ctr*ract;
	cti = -cti*ract;
	ptr = cinur*ract;
	pti = cinui*ract;
	cinur = ptr*ctr - pti*cti;
	cinui = ptr*cti + pti*ctr;
	YR[0] = cinur*csclr;
	YI[0] = cinui*csclr;
	if(n==1) return;
	for(i=2; i<=n; i++) { //DO 40
		ptr = str*cinur - sti*cinui;
		cinui = str*cinui + sti*cinur;
		cinur = ptr;
		str = YR[i-1];
		sti = YI[i-1];
		YR[i-1] = cinur*csclr;
		YI[i-1] = cinui*csclr;
	} //CONTINUE 40
	return;
WR50:
	*NZ = -1;
	if(nw==(-2)) *NZ = -2;
	return;
}
//use: casyi, cseri, cmlri, cbknu
void zacai(double zr, double zi, double fnu, int kode, int mr, int n, double *YR, double *YI, int *NZ, double rl, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zacai\n");
	double arg, ascle, az, csgni, csgnr, cspni, cspnr, c1i, c1r, c2i, c2r, dfnu, fmr, sgn, yy, zni, znr;
	double cyi[2], cyr[2];
	int    inu, iuf, nn, nw;

	*NZ = 0;
	znr = -zr;
	zni = -zi;
	az = zabs(zr,zi);
	nn = n;
	dfnu = fnu + (double)(n-1);
	if(az<=2.0) goto AC10;
	if(az*az*0.25>dfnu+1.0) goto AC20;
AC10:
//C-----------------------------------------------------------------------
//C     POWER SERIES FOR THE I FUNCTION
//C-----------------------------------------------------------------------
	zseri(znr, zni, fnu, kode, nn, YR, YI, &nw, tol, elim, alim, debug);
	goto AC40;
AC20:
	if(az<rl) goto AC30;
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR LARGE Z FOR THE I FUNCTION
//C-----------------------------------------------------------------------
	zasyi(znr, zni, fnu, kode, nn, YR, YI, &nw, rl, tol, elim, alim, debug);
	if(nw<0) goto AC80;
	goto AC40;
AC30:
//C-----------------------------------------------------------------------
//C     MILLER ALGORITHM NORMALIZED BY THE SERIES FOR THE I FUNCTION
//C-----------------------------------------------------------------------
	zmlri(znr, zni, fnu, kode, nn, YR, YI, &nw, tol, debug);
	if(nw<0) goto AC80;
AC40:
//C-----------------------------------------------------------------------
//C     ANALYTIC CONTINUATION TO THE LEFT HALF PLANE FOR THE K FUNCTION
//C-----------------------------------------------------------------------
	zbknu(znr, zni, fnu, kode, 1, cyr, cyi, &nw, tol, elim, alim, debug);
	if(nw!=0) goto AC80;
	fmr = (double)mr;
	sgn = -dsign(_PI_,fmr);
	csgnr = 0.0;
	csgni = sgn;
	if(kode==1) goto AC50;
	yy = -zni;
	csgnr = -csgni*std::sin(yy);
	csgni = csgni*std::cos(yy);
AC50:
//C-----------------------------------------------------------------------
//C     CALCULATE CSPN=EXP(FNU*PI*I) TO MINIMIZE LOSSES OF SIGNIFICANCE
//C     WHEN FNU IS LARGE
//C-----------------------------------------------------------------------
	inu = (int)fnu;
	arg = (fnu-(double)inu)*sgn;
	cspnr = std::cos(arg);
	cspni = std::sin(arg);
	if((inu&1)==0) goto AC60;
	cspnr = -cspnr;
	cspni = -cspni;
AC60:
	c1r = cyr[0];
	c1i = cyi[0];
	c2r = YR[0];
	c2i = YI[0];
	if(kode==1) goto AC70;
	iuf = 0;
	ascle = 1000.0*D1MACH[0]/tol;
	zs1s2(znr, zni, &c1r, &c1i, &c2r, &c2i, &nw, ascle, alim, &iuf, debug);
	*NZ = *NZ + nw;
AC70:
	YR[0] = cspnr*c1r - cspni*c1i + csgnr*c2r - csgni*c2i;
	YI[0] = cspnr*c1i + cspni*c1r + csgnr*c2i + csgni*c2r;
	return;
AC80:
	*NZ = -1;
	if(nw==(-2)) *NZ = -2;
	return;
}
//use: cacai, cbknu
void zairy(double zr, double zi, int id, int kode, double *AIR, double *AII, int *NZ, int *IERR, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zairy\n");
	double aa, ad, ak, alaz, alim, atrm, az, az3, bb, bk, cc, ck, coef, csqi, csqr, \
	       dig, dk, d1, d2, elim, fid, fnu, ptr, rl, r1m5, sfac, sti, str, s1i, s1r, \
	       s2i, s2r, tol, trm1i, trm1r, trm2i, trm2r, tth, ztai, ztar, z3i, z3r;
	double cyi[2], cyr[2];
	int    iflag, k, k1, k2, mr, nn;

	coef = 0.18377629847393068317044216610432314713246216012221355093312200676367676782; // 1.0/(sqrt(3)*PI)
	tth  = 2.0/3.0;

	*IERR = 0;
	*NZ = 0;
	if(id<0 || id>1) *IERR = 1;
	if(kode<1 || kode>2) *IERR = 1;
	if(*IERR!=0) return;
	az = zabs(zr,zi);
	tol = std::max(D1MACH[3],1.0e-18);
	fid = (double)id;
	if(az>1.0) goto AI70;
//C-----------------------------------------------------------------------
//C     POWER SERIES FOR CABS(Z).LE.1.
//C-----------------------------------------------------------------------
	s1r = CONER;
	s1i = CONEI;
	s2r = CONER;
	s2i = CONEI;
	if(az<tol) goto AI170;
	aa = az*az;
	if(aa<tol/az) goto AI40;
	trm1r = CONER;
	trm1i = CONEI;
	trm2r = CONER;
	trm2i = CONEI;
	atrm = 1.0;
	str = zr*zr - zi*zi;
	sti = zr*zi + zi*zr;
	z3r = str*zr - sti*zi;
	z3i = str*zi + sti*zr;
	az3 = az*aa;
	ak = 2.0 + fid;
	bk = 3.0 - fid - fid;
	ck = 4.0 - fid;
	dk = 3.0 + fid + fid;
	d1 = ak*dk;
	d2 = bk*ck;
	ad = std::min(d1,d2);
	ak = 24.0 + 9.0*fid;
	bk = 30.0 - 9.0*fid;
	for(k=1; k<=25; k++) { //DO 30
		str = (trm1r*z3r-trm1i*z3i)/d1;
		trm1i = (trm1r*z3i+trm1i*z3r)/d1;
		trm1r = str;
		s1r = s1r + trm1r;
		s1i = s1i + trm1i;
		str = (trm2r*z3r-trm2i*z3i)/d2;
		trm2i = (trm2r*z3i+trm2i*z3r)/d2;
		trm2r = str;
		s2r = s2r + trm2r;
		s2i = s2i + trm2i;
		atrm = atrm*az3/ad;
		d1 = d1 + ak;
		d2 = d2 + bk;
		ad = std::min(d1,d2);
		if(atrm<tol*ad) goto AI40;
		ak = ak + 18.0;
		bk = bk + 18.0;
	} //CONTINUE 30
AI40:
	if(id==1) goto AI50;
	*AIR = s1r*AI0 - AIP0*(zr*s2r-zi*s2i);
	*AII = s1i*AI0 - AIP0*(zr*s2i+zi*s2r);
	if(kode==1) return;
	zsqrt(zr, zi, &str, &sti);
	ztar = tth*(zr*str-zi*sti);
	ztai = tth*(zr*sti+zi*str);
	zexp(ztar, ztai, &str, &sti);
	ptr = *AIR*str - *AII*sti;
	*AII = *AIR*sti + *AII*str;
	*AIR = ptr;
	return;
AI50:
	*AIR = -s2r*AIP0;
	*AII = -s2i*AIP0;
	if(az<=tol) goto AI60;
	str = zr*s1r - zi*s1i;
	sti = zr*s1i + zi*s1r;
	cc = AI0/(1.0+fid);
	*AIR = *AIR + cc*(str*zr-sti*zi);
	*AII = *AII + cc*(str*zi+sti*zr);
AI60:
	if(kode==1) return;
	zsqrt(zr, zi, &str, &sti);
	ztar = tth*(zr*str-zi*sti);
	ztai = tth*(zr*sti+zi*str);
	zexp(ztar, ztai, &str, &sti);
	ptr = *AIR*str - *AII*sti;
	*AII = *AII*str + *AIR*sti;
	*AIR = ptr;
	return;
//C-----------------------------------------------------------------------
//C     CASE FOR CABS(Z).GT.1.0
//C-----------------------------------------------------------------------
AI70:
	fnu = (1.0+fid)/3.0;
//C-----------------------------------------------------------------------
//C     SET PARAMETERS RELATED TO MACHINE CONSTANTS.
//C     TOL IS THE APPROXIMATE UNIT ROUNDOFF LIMITED TO 1.0D-18.
//C     ELIM IS THE APPROXIMATE EXPONENTIAL OVER- AND UNDERFLOW LIMIT.
//C     EXP(-ELIM).LT.EXP(-ALIM)=EXP(-ELIM)/TOL    AND
//C     EXP(ELIM).GT.EXP(ALIM)=EXP(ELIM)*TOL       ARE INTERVALS NEAR
//C     UNDERFLOW AND OVERFLOW LIMITS WHERE SCALED ARITHMETIC IS DONE.
//C     RL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC EXPANSION FOR LARGE Z.
//C     DIG = NUMBER OF BASE 10 DIGITS IN TOL = 10**(-DIG).
//C-----------------------------------------------------------------------
	k1 = I1MACH[14];
	k2 = I1MACH[15];
	r1m5 = D1MACH[4];
	k = std::min(std::abs(k1),std::abs(k2));
	elim = LN10*((double)k*r1m5-3.0); //2.303*
	k1 = I1MACH[13] - 1;
	aa = r1m5*(double)k1;
	dig = std::min(aa,18.0);
	aa = aa*LN10; //*2.303
	alim = elim + std::max(-aa,-41.45);
	rl = 1.2*dig + 3.0;
	alaz = std::log(az);
//C--------------------------------------------------------------------------
//C     TEST FOR PROPER RANGE
//C-----------------------------------------------------------------------
	aa = 0.5/tol;
	bb = (double)I1MACH[8]*0.5;
	aa = std::min(aa,bb);
	aa = std::cbrt(aa); //AA**TTH;
	if(az>aa*aa) goto AI260;
//	AA = std::sqrt(AA);
	if(az>aa) *IERR = 3;
	zsqrt(zr, zi, &csqr, &csqi);
	ztar = tth*(zr*csqr-zi*csqi);
	ztai = tth*(zr*csqi+zi*csqr);
//C-----------------------------------------------------------------------
//C     RE(ZTA).LE.0 WHEN RE(Z).LT.0, ESPECIALLY WHEN IM(Z) IS SMALL
//C-----------------------------------------------------------------------
	iflag = 0;
	sfac = 1.0;
	ak = ztai;
	if(zr>=0.0) goto AI80;
	bk = ztar;
	ck = -std::abs(bk);
	ztar = ck;
	ztai = ak;
AI80:
	if(zi!=0.0) goto AI90;
	if(zr>0.0) goto AI90;
	ztar = 0.0;
	ztai = ak;
AI90:
	aa = ztar;
	if(aa>=0.0 && zr>0.0) goto AI110;
	if(kode==2) goto AI100;
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST
//C-----------------------------------------------------------------------
	if(aa>(-alim)) goto AI100;
	aa = -aa + 0.25*alaz;
	iflag = 1;
	sfac = tol;
	if(aa>elim) goto AI270;
AI100:
//C-----------------------------------------------------------------------
//C     CBKNU AND CACON RETURN EXP(ZTA)*K(FNU,ZTA) ON KODE=2
//C-----------------------------------------------------------------------
	mr = 1;
	if(zi<0.0) mr = -1;
	zacai(ztar, ztai, fnu, kode, mr, 1, cyr, cyi, &nn, rl, tol, elim, alim, debug);
	if(nn<0) goto AI280;
	*NZ = *NZ + nn;
	goto AI130;
AI110:
	if(kode==2) goto AI120;
//C-----------------------------------------------------------------------
//C     UNDERFLOW TEST
//C-----------------------------------------------------------------------
	if(aa<alim) goto AI120;
	aa = -aa - 0.25*alaz;
	iflag = 2;
	sfac = 1.0/tol;
	if(aa<(-elim)) goto AI210;
AI120:
	zbknu(ztar, ztai, fnu, kode, 1, cyr, cyi, NZ, tol, elim, alim, debug);
AI130:
	s1r = cyr[0]*coef;
	s1i = cyi[0]*coef;
	if(iflag!=0) goto AI150;
	if(id==1) goto AI140;
	*AIR = csqr*s1r - csqi*s1i;
	*AII = csqr*s1i + csqi*s1r;
	return;
AI140:
	*AIR = -(zr*s1r-zi*s1i);
	*AII = -(zr*s1i+zi*s1r);
	return;
AI150:
	s1r = s1r*sfac;
	s1i = s1i*sfac;
	if(id==1) goto AI160;
	str = s1r*csqr - s1i*csqi;
	s1i = s1r*csqi + s1i*csqr;
	s1r = str;
	*AIR = s1r/sfac;
	*AII = s1i/sfac;
	return;
AI160:
	str = -(s1r*zr-s1i*zi);
	s1i = -(s1r*zi+s1i*zr);
	s1r = str;
	*AIR = s1r/sfac;
	*AII = s1i/sfac;
	return;
AI170:
	aa = 1000.0*D1MACH[0];
	s1r = CZEROR;
	s1i = CZEROI;
	if(id==1) goto AI190;
	if(az<=aa) goto AI180;
	s1r = AIP0*zr;
	s1i = AIP0*zi;
AI180:
	*AIR = AI0 - s1r;
	*AII = -s1i;
	return;
AI190:
	*AIR = -AIP0;
	*AII = 0.0;
	aa = std::sqrt(aa);
	if(az<=aa) goto AI200;
	s1r = 0.5*(zr*zr-zi*zi);
	s1i = zr*zi;
AI200:
	*AIR = *AIR + AI0*s1r;
	*AII = *AII + AI0*s1i;
	return;
AI210:
	*NZ = 1;
	*AIR = CZEROR;
	*AII = CZEROI;
	return;
AI260:
	*IERR = 4;
	*NZ = 0;
	return;
AI270:
	*NZ = 0;
	*IERR = 2;
	return;
AI280:
	if(nn==(-1)) goto AI270;
	*NZ = 0;
	*IERR = 5;
	return;
}
//use: cs1s2, cuchk, cunik
void zunk1(double zr, double zi, double fnu, int kode, int mr, int n, double *YR, double *YI, int *NZ, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called znuk1\n");
	double ang, aphi, asc, ascle, cki, ckr, crsc, cscl, csgni, cspni, cspnr, csr, c1i, c1r, c2i, c2m, c2r, \
		   fmr, fn, fnf, phidi, phidr, rast, razr, rs1, rzi, rzr, sgn, sti, str, sumdi, sumdr, \
	       s1i, s1r, s2i, s2r, zet1di, zet1dr, zet2di, zet2dr, zri, zrr;
	double bry[3], csrr[3], cssr[3], cyi[2], cyr[2], phii[2], phir[2], sumi[2], sumr[2], \
	       zeta1i[2], zeta1r[2], zeta2i[2], zeta2r[2];
	double cworki[16][3], cworkr[16][3];
	int    i, ib, ic, iflag, ifn, il, initd, inu, ipard, iuf, j, k, kdflg, kflag, kk, m, nw;
	int    init[2];

	//initialize, so the compiler is happy
	iflag = 1;
	kflag = 1;
	fn = 0.0;
	//end of extra initialization

	kdflg = 1;
	*NZ = 0;
//C-----------------------------------------------------------------------
//C     EXP(-ALIM)=EXP(-ELIM)/TOL=APPROX. ONE PRECISION GREATER THAN
//C     THE UNDERFLOW LIMIT
//C-----------------------------------------------------------------------
	cscl = 1.0/tol;
	crsc = tol;
	cssr[0] = cscl;
	cssr[1] = CONER;
	cssr[2] = crsc;
	csrr[0] = crsc;
	csrr[1] = CONER;
	csrr[2] = cscl;
	bry[0] = 1000.0*D1MACH[0]/tol;
	bry[1] = 1.0/bry[0];
	bry[2] = D1MACH[1];
	zrr = zr;
	zri = zi;
	if(zr>=0.0) goto KO10;
	zrr = -zr;
	zri = -zi;
KO10:
	j = 2;
	for(i=1; i<=n; i++) { //DO 70
//C-----------------------------------------------------------------------
//C     J FLIP FLOPS BETWEEN 1 AND 2 IN J = 3 - J
//C-----------------------------------------------------------------------
		j = 3 - j;
		fn = fnu + (double)(i-1);
		init[j-1] = 0;
		zunik(zrr, zri, fn, 2, 0, tol, &(init[j-1]), &(phir[j-1]), &(phii[j-1]), \
		      &(zeta1r[j-1]), &(zeta1i[j-1]), &(zeta2r[j-1]), &(zeta2i[j-1]), \
			  &(sumr[j-1]), &(sumi[j-1]), &(cworkr[0][j-1]), &(cworki[0][j-1]), debug);
		if(kode==1) goto KO20;
		str = zrr + zeta2r[j-1];
		sti = zri + zeta2i[j-1];
		rast = fn/zabs(str,sti);
		str = str*rast*rast;
		sti = -sti*rast*rast;
		s1r = zeta1r[j-1] - str;
		s1i = zeta1i[j-1] - sti;
		goto KO30;
KO20:
		s1r = zeta1r[j-1] - zeta2r[j-1];
		s1i = zeta1i[j-1] - zeta2i[j-1];
KO30:
		rs1 = s1r;
//C-----------------------------------------------------------------------
//C     TEST FOR UNDERFLOW AND OVERFLOW
//C-----------------------------------------------------------------------
		if(std::abs(rs1)>elim) goto KO60;
		if(kdflg==1) kflag = 2;
		if(std::abs(rs1)<alim) goto KO40;
//C-----------------------------------------------------------------------
//C     REFINE  TEST AND SCALE
//C-----------------------------------------------------------------------
		aphi = zabs(phir[j-1],phii[j-1]);
		rs1 = rs1 + std::log(aphi);
		if(std::abs(rs1)>elim) goto KO60;
		if(kdflg==1) kflag = 1;
		if(rs1<0.0) goto KO40;
		if(kdflg==1) kflag = 3;
KO40:
//C-----------------------------------------------------------------------
//C     SCALE S1 TO KEEP INTERMEDIATE ARITHMETIC ON SCALE NEAR
//C     EXPONENT EXTREMES
//C-----------------------------------------------------------------------
		s2r = phir[j-1]*sumr[j-1] - phii[j-1]*sumi[j-1];
		s2i = phir[j-1]*sumi[j-1] + phii[j-1]*sumr[j-1];
		str = std::exp(s1r)*cssr[kflag-1];
		s1r = str*std::cos(s1i);
		s1i = str*std::sin(s1i);
		str = s2r*s1r - s2i*s1i;
		s2i = s1r*s2i + s2r*s1i;
		s2r = str;
		if(kflag!=1) goto KO50;
		zuchk(s2r, s2i, &nw, bry[0], tol, debug);
		if(nw!=0) goto KO60;
KO50:
		cyr[kdflg-1] = s2r;
		cyi[kdflg-1] = s2i;
		YR[i-1] = s2r*csrr[kflag-1];
		YI[i-1] = s2i*csrr[kflag-1];
		if(kdflg==2) goto KO75;
		kdflg = 2;
		continue; // GO TO 70
KO60:
		if(rs1>0.0) goto KO300;
//C-----------------------------------------------------------------------
//C     FOR ZR.LT.0.0, THE I FUNCTION TO BE ADDED WILL OVERFLOW
//C-----------------------------------------------------------------------
		if(zr<0.0) goto KO300;
		kdflg = 1;
		YR[i-1]=CZEROR;
		YI[i-1]=CZEROI;
		*NZ = *NZ + 1;
		if(i==1) continue; // GO TO 70
		if((YR[i-2]==CZEROR) && (YI[i-2]==CZEROI)) continue; // GO TO 70
		YR[i-2]=CZEROR;
		YI[i-2]=CZEROI;
		*NZ = *NZ + 1;
	} //CONTINUE 70
	i = n;
KO75:
	razr = 1.0/zabs(zrr,zri);
	str = zrr*razr;
	sti = -zri*razr;
	rzr = (str+str)*razr;
	rzi = (sti+sti)*razr;
	ckr = fn*rzr;
	cki = fn*rzi;
	ib = i + 1;
	if(n<ib) goto KO160;
//C-----------------------------------------------------------------------
//C     TEST LAST MEMBER FOR UNDERFLOW AND OVERFLOW. SET SEQUENCE TO ZERO
//C     ON UNDERFLOW.
//C-----------------------------------------------------------------------
	fn = fnu + (double)(n-1);
	ipard = 1;
	if(mr!=0) ipard = 0;
	initd = 0;
	zunik(zrr, zri, fn, 2, ipard, tol, &initd, &phidr, &phidi, &zet1dr, &zet1di, \
	      &zet2dr, &zet2di, &sumdr, &sumdi, &(cworkr[0][2]), &(cworki[0][2]), debug);
	if(kode==1) goto KO80;
	str = zrr + zet2dr;
	sti = zri + zet2di;
	rast = fn/zabs(str,sti);
	str = str*rast*rast;
	sti = -sti*rast*rast;
	s1r = zet1dr - str;
	s1i = zet1di - sti;
	goto KO90;
KO80:
	s1r = zet1dr - zet2dr;
	s1i = zet1di - zet2di;
KO90:
	rs1 = s1r;
	if(std::abs(rs1)>elim) goto KO95;
	if(std::abs(rs1)<alim) goto KO100;
//C----------------------------------------------------------------------------
//C     REFINE ESTIMATE AND TEST
//C-------------------------------------------------------------------------
	aphi = zabs(phidr,phidi);
	rs1 = rs1+std::log(aphi);
	if(std::abs(rs1)<elim) goto KO100;
KO95:
	if(std::abs(rs1)>0.0) goto KO300;
//C-----------------------------------------------------------------------
//C     FOR ZR.LT.0.0, THE I FUNCTION TO BE ADDED WILL OVERFLOW
//C-----------------------------------------------------------------------
	if(zr<0.0) goto KO300;
	*NZ = n;
	for(i=1; i<=n; i++) { //DO 96
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 96
	return;
//C---------------------------------------------------------------------------
//C     FORWARD RECUR FOR REMAINDER OF THE SEQUENCE
//C----------------------------------------------------------------------------
KO100:
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	c1r = csrr[kflag-1];
	ascle = bry[kflag-1];
	for(i=ib; i<=n; i++) { //DO 120
		c2r = s2r;
		c2i = s2i;
		s2r = ckr*c2r - cki*c2i + s1r;
		s2i = ckr*c2i + cki*c2r + s1i;
		s1r = c2r;
		s1i = c2i;
		ckr = ckr + rzr;
		cki = cki + rzi;
		c2r = s2r*c1r;
		c2i = s2i*c1r;
		YR[i-1] = c2r;
		YI[i-1] = c2i;
		if(kflag>=3) continue; // GO TO 120
		str = std::abs(c2r);
		sti = std::abs(c2i);
		c2m = std::max(str,sti);
		if(c2m<=ascle) continue; // GO TO 120
		kflag = kflag + 1;
		ascle = bry[kflag-1];
		s1r = s1r*c1r;
		s1i = s1i*c1r;
		s2r = c2r;
		s2i = c2i;
		s1r = s1r*cssr[kflag-1];
		s1i = s1i*cssr[kflag-1];
		s2r = s2r*cssr[kflag-1];
		s2i = s2i*cssr[kflag-1];
		c1r = csrr[kflag-1];
	} //CONTINUE 120
KO160:
	if(mr==0) return;
//C-----------------------------------------------------------------------
//C     ANALYTIC CONTINUATION FOR RE(Z).LT.0.0D0
//C-----------------------------------------------------------------------
	*NZ = 0;
	fmr = (double)mr;
	sgn = -dsign(_PI_,fmr);
//C-----------------------------------------------------------------------
//C     CSPN AND CSGN ARE COEFF OF K AND I FUNCTIONS RESP.
//C-----------------------------------------------------------------------
	csgni = sgn;
	inu = (int)fnu;
	fnf = fnu - (double)inu;
	ifn = inu + n - 1;
	ang = fnf*sgn;
	cspnr = std::cos(ang);
	cspni = std::sin(ang);
	if((ifn&1)==0) goto KO170;
	cspnr = -cspnr;
	cspni = -cspni;
KO170:
	asc = bry[0];
	iuf = 0;
	kk = n;
	kdflg = 1;
	ib = ib - 1;
	ic = ib - 1;
	for(k=1; k<=n; k++) { //DO 270
		fn = fnu + (double)(kk-1);
//C-----------------------------------------------------------------------
//C     LOGIC TO SORT OUT CASES WHOSE PARAMETERS WERE SET FOR THE K
//C     FUNCTION ABOVE
//C-----------------------------------------------------------------------
		m = 3;
		if(n>2) goto KO175;
KO172:
		initd = init[j-1];
		phidr = phir[j-1];
		phidi = phii[j-1];
		zet1dr = zeta1r[j-1];
		zet1di = zeta1i[j-1];
		zet2dr = zeta2r[j-1];
		zet2di = zeta2i[j-1];
		sumdr = sumr[j-1];
		sumdi = sumi[j-1];
		m = j;
		j = 3 - j;
		goto KO180;
KO175:
		if((kk==n) && (ib<n)) goto KO180;
		if((kk==ib) || (kk==ic)) goto KO172;
		initd = 0;
KO180:
		zunik(zrr, zri, fn, 1, 0, tol, &initd, &phidr, &phidi, &zet1dr, &zet1di, \
		      &zet2dr, &zet2di, &sumdr, &sumdi, &(cworkr[0][m-1]), &(cworki[0][m-1]), debug);
		if(kode==1) goto KO200;
		str = zrr + zet2dr;
		sti = zri + zet2di;
		rast = fn/zabs(str,sti);
		str = str*rast*rast;
		sti = -sti*rast*rast;
		s1r = -zet1dr + str;
		s1i = -zet1di + sti;
		goto KO210;
KO200:
		s1r = -zet1dr + zet2dr;
		s1i = -zet1di + zet2di;
KO210:
//C-----------------------------------------------------------------------
//C     TEST FOR UNDERFLOW AND OVERFLOW
//C-----------------------------------------------------------------------
		rs1 = s1r;
		if(std::abs(rs1)>elim) goto KO260;
		if(kdflg==1) iflag = 2;
		if(std::abs(rs1)<alim) goto KO220;
//C-----------------------------------------------------------------------
//C     REFINE  TEST AND SCALE
//C-----------------------------------------------------------------------
		aphi = zabs(phidr,phidi);
		rs1 = rs1 + std::log(aphi);
		if(std::abs(rs1)>elim) goto KO260;
		if(kdflg==1) iflag = 1;
		if(rs1<0.0) goto KO220;
		if(kdflg==1) iflag = 3;
KO220:
		str = phidr*sumdr - phidi*sumdi;
		sti = phidr*sumdi + phidi*sumdr;
		s2r = -csgni*sti;
		s2i = csgni*str;
		str = std::exp(s1r)*cssr[iflag-1];
		s1r = str*std::cos(s1i);
		s1i = str*std::sin(s1i);
		str = s2r*s1r - s2i*s1i;
		s2i = s2r*s1i + s2i*s1r;
		s2r = str;
		if(iflag!=1) goto KO230;
		zuchk(s2r, s2i, &nw, bry[0], tol, debug);
		if(nw==0) goto KO230;
		s2r = CZEROR;
		s2i = CZEROI;
KO230:
		cyr[kdflg-1] = s2r;
		cyi[kdflg-1] = s2i;
		c2r = s2r;
		c2i = s2i;
		s2r = s2r*csrr[iflag-1];
		s2i = s2i*csrr[iflag-1];
//C-----------------------------------------------------------------------
//C     ADD I AND K FUNCTIONS, K SEQUENCE IN Y(I), I=1,N
//C-----------------------------------------------------------------------
		s1r = YR[kk-1];
		s1i = YI[kk-1];
		if(kode==1) goto KO250;
		zs1s2(zrr, zri, &s1r, &s1i, &s2r, &s2i, &nw, asc, alim, &iuf, debug);
		*NZ = *NZ + nw;
KO250:
		YR[kk-1] = s1r*cspnr - s1i*cspni + s2r;
		YI[kk-1] = cspnr*s1i + cspni*s1r + s2i;
		kk = kk - 1;
		cspnr = -cspnr;
		cspni = -cspni;
		if(c2r!=0.0 || c2i!=0.0) goto KO255;
		kdflg = 1;
		continue; // GO TO 270
KO255:
		if(kdflg==2) goto KO275;
		kdflg = 2;
		continue; // GO TO 270
KO260:
		if(rs1>0.0) goto KO300;
		s2r = CZEROR;
		s2i = CZEROI;
		goto KO230;
	} //CONTINUE 270
	k = n;
KO275:
	il = n - k;
	if(il==0) return;
//C-----------------------------------------------------------------------
//C     RECUR BACKWARD FOR REMAINDER OF I SEQUENCE AND ADD IN THE
//C     K FUNCTIONS, SCALING THE I SEQUENCE DURING RECURRENCE TO KEEP
//C     INTERMEDIATE ARITHMETIC ON SCALE NEAR EXPONENT EXTREMES.
//C-----------------------------------------------------------------------
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	csr = csrr[iflag-1];
	ascle = bry[iflag-1];
	fn = (double)(inu+il);
	for(i=1; i<=il; i++) { //DO 290
		c2r = s2r;
		c2i = s2i;
		s2r = s1r + (fn+fnf)*(rzr*c2r-rzi*c2i);
		s2i = s1i + (fn+fnf)*(rzr*c2i+rzi*c2r);
		s1r = c2r;
		s1i = c2i;
		fn = fn - 1.0;
		c2r = s2r*csr;
		c2i = s2i*csr;
		ckr = c2r;
		cki = c2i;
		c1r = YR[kk-1];
		c1i = YI[kk-1];
		if(kode==1) goto KO280;
		zs1s2(zrr, zri, &c1r, &c1i, &c2r, &c2i, &nw, asc, alim, &iuf, debug);
		*NZ = *NZ + nw;
KO280:
		YR[kk-1] = c1r*cspnr - c1i*cspni + c2r;
		YI[kk-1] = c1r*cspni + c1i*cspnr + c2i;
		kk = kk - 1;
		cspnr = -cspnr;
		cspni = -cspni;
		if(iflag>=3) continue; // GO TO 290
		c2r = std::abs(ckr);
		c2i = std::abs(cki);
		c2m = std::max(c2r,c2i);
		if(c2m<=ascle) continue; // GO TO 290
		iflag = iflag + 1;
		ascle = bry[iflag-1];
		s1r = s1r*csr;
		s1i = s1i*csr;
		s2r = ckr;
		s2i = cki;
		s1r = s1r*cssr[iflag-1];
		s1i = s1i*cssr[iflag-1];
		s2r = s2r*cssr[iflag-1];
		s2i = s2i*cssr[iflag-1];
		csr = csrr[iflag-1];
	} //CONTINUE 290
	return;
KO300:
	*NZ = -1;
	return;
}
//use: cairy, cs1s2, cuchk, cunhj
void zunk2(double zr, double zi, double fnu, int kode, int mr, int n, double *YR, double *YI, int *NZ, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called znuk2\n");
	double aarg, aii, air, ang, aphi, argdi, argdr, asc, ascle, sumdi, asumdr, bsumdi, bsumdr,  \
	       car, cki, ckr, crsc, cr1i, cr1r, cr2i, cr2r, cscl, csgni, csi, cspni, cspnr, csr, c1i, c1r, \
	       c2i, c2m, c2r, daii, dair, fmr, fn, fnf, phidi, phidr, pti, ptr, rast, razr, rs1, rzi, rzr, \
	       sar, sgn, sti, str, s1i, s1r, s2i, s2r, yy, zbi, zbr, zet1di, zet1dr, zet2di, zet2dr, \
		   zni, znr, zri, zrr;
	double argi[2], argr[2], asumi[2], asumr[2], bry[3], bsumi[2], bsumr[2], cipi[4], cipr[4], csrr[3], \
	       cssr[3], cyi[2], cyr[2], phii[2], phir[2], zeta1i[2], zeta1r[2], zeta2i[2], zeta2r[2];
	int    i, ib, ic, idum, iflag, ifn, il, in, inu, ipard, iuf, j, k, kdflg, kflag, kk, nai, ndai, nw;

	//initialize, so the compiler is happy
	iflag = 1;
	kflag = 1;
	fn = 0.0;
	//end of extra initialization

	cr1r = 1.0;
	cr1i = RT3;
	cr2r = -0.5;
	cr2i = -0.5*RT3;
	cipr[0] =  1.0; cipi[0] =  0.0;
	cipr[1] =  0.0; cipi[1] = -1.0;
	cipr[2] = -1.0; cipi[2] =  0.0;
	cipr[3] =  0.0; cipi[3] =  1.0;

	kdflg = 1;
	*NZ = 0;
//C-----------------------------------------------------------------------
//C     EXP(-ALIM)=EXP(-ELIM)/TOL=APPROX. ONE PRECISION GREATER THAN
//C     THE UNDERFLOW LIMIT
//C-----------------------------------------------------------------------
	cscl = 1.0/tol;
	crsc = tol;
	cssr[0] = cscl;
	cssr[1] = CONER;
	cssr[2] = crsc;
	csrr[0] = crsc;
	csrr[1] = CONER;
	csrr[2] = cscl;
	bry[0] = 1000.0*D1MACH[0]/tol;
	bry[1] = 1.0/bry[0];
	bry[2] = D1MACH[1];
	zrr = zr;
	zri = zi;
	if(zr>=0.0) goto KT10;
	zrr = -zr;
	zri = -zi;
KT10:
	yy = zri;
	znr = zri;
	zni = -zrr;
	zbr = zrr;
	zbi = zri;
	inu = (int)fnu;
	fnf = fnu - (double)inu;
	ang = -HPI*fnf;
	car = std::cos(ang);
	sar = std::sin(ang);
	c2r = HPI*sar;
	c2i = -HPI*car;
	kk = (inu&3) + 1;
	str = c2r*cipr[kk-1] - c2i*cipi[kk-1];
	sti = c2r*cipi[kk-1] + c2i*cipr[kk-1];
	csr = cr1r*str - cr1i*sti;
	csi = cr1r*sti + cr1i*str;
	if(yy>0.0) goto KT20;
	znr = -znr;
	zbi = -zbi;
KT20:
//C-----------------------------------------------------------------------
//C     K(FNU,Z) IS COMPUTED FROM H(2,FNU,-I*Z) WHERE Z IS IN THE FIRST
//C     QUADRANT. FOURTH QUADRANT VALUES (YY.LE.0.0E0) ARE COMPUTED BY
//C     CONJUGATION SINCE THE K FUNCTION IS REAL ON THE POSITIVE REAL AXIS
//C-----------------------------------------------------------------------
	j = 2;
	for(i=1; i<=n; i++) { //DO 80
//C-----------------------------------------------------------------------
//C     J FLIP FLOPS BETWEEN 1 AND 2 IN J = 3 - J
//C-----------------------------------------------------------------------
		j = 3 - j;
		fn = fnu + (double)(i-1);
		zunhj(znr, zni, fn, 0, tol, &(phir[j-1]), &(phii[j-1]), &(argr[j-1]), &(argi[j-1]), \
		      &(zeta1r[j-1]), &(zeta1i[j-1]), &(zeta2r[j-1]), &(zeta2i[j-1]), \
			  &(asumr[j-1]), &(asumi[j-1]), &(bsumr[j-1]), &(bsumi[j-1]), debug);
		if(kode==1) goto KT30;
		str = zbr + zeta2r[j-1];
		sti = zbi + zeta2i[j-1];
		rast = fn/zabs(str,sti);
		str = str*rast*rast;
		sti = -sti*rast*rast;
		s1r = zeta1r[j-1] - str;
		s1i = zeta1i[j-1] - sti;
		goto KT40;
KT30:
		s1r = zeta1r[j-1] - zeta2r[j-1];
		s1i = zeta1i[j-1] - zeta2i[j-1];
KT40:
//C-----------------------------------------------------------------------
//C     TEST FOR UNDERFLOW AND OVERFLOW
//C-----------------------------------------------------------------------
		rs1 = s1r;
		if(std::abs(rs1)>elim) goto KT70;
		if(kdflg==1) kflag = 2;
		if(std::abs(rs1)<alim) goto KT50;
//C-----------------------------------------------------------------------
//C     REFINE  TEST AND SCALE
//C-----------------------------------------------------------------------
		aphi = zabs(phir[j-1],phii[j-1]);
		aarg = zabs(argr[j-1],argi[j-1]);
		rs1 = rs1 + std::log(aphi) - 0.25*std::log(aarg) - AIC;
		if(std::abs(rs1)>elim) goto KT70;
		if(kdflg==1) kflag = 1;
		if(rs1<0.0) goto KT50;
		if(kdflg==1) kflag = 3;
KT50:
//C-----------------------------------------------------------------------
//C     SCALE S1 TO KEEP INTERMEDIATE ARITHMETIC ON SCALE NEAR
//C     EXPONENT EXTREMES
//C-----------------------------------------------------------------------
		c2r = argr[j-1]*cr2r - argi[j-1]*cr2i;
		c2i = argr[j-1]*cr2i + argi[j-1]*cr2r;
		zairy(c2r, c2i, 0, 2, &air, &aii, &nai, &idum, debug);
		zairy(c2r, c2i, 1, 2, &dair, &daii, &ndai, &idum, debug);
		str = dair*bsumr[j-1] - daii*bsumi[j-1];
		sti = dair*bsumi[j-1] + daii*bsumr[j-1];
		ptr = str*cr2r - sti*cr2i;
		pti = str*cr2i + sti*cr2r;
		str = ptr + (air*asumr[j-1]-aii*asumi[j-1]);
		sti = pti + (air*asumi[j-1]+aii*asumr[j-1]);
		ptr = str*phir[j-1] - sti*phii[j-1];
		pti = str*phii[j-1] + sti*phir[j-1];
		s2r = ptr*csr - pti*csi;
		s2i = ptr*csi + pti*csr;
		str = std::exp(s1r)*cssr[kflag-1];
		s1r = str*std::cos(s1i);
		s1i = str*std::sin(s1i);
		str = s2r*s1r - s2i*s1i;
		s2i = s1r*s2i + s2r*s1i;
		s2r = str;
		if(kflag!=1) goto KT60;
		zuchk(s2r, s2i, &nw, bry[0], tol, debug);
		if(nw!=0) goto KT70;
KT60:
		if(yy<=0.0) s2i = -s2i;
		cyr[kdflg-1] = s2r;
		cyi[kdflg-1] = s2i;
		YR[i-1] = s2r*csrr[kflag-1];
		YI[i-1] = s2i*csrr[kflag-1];
		str = csi;
		csi = -csr;
		csr = str;
		if(kdflg==2) goto KT85;
		kdflg = 2;
		continue; // GO TO 80
KT70:
		if(rs1>0.0) goto KT320;
//C-----------------------------------------------------------------------
//C     FOR ZR.LT.0.0, THE I FUNCTION TO BE ADDED WILL OVERFLOW
//C-----------------------------------------------------------------------
		if(zr<0.0) goto KT320;
		kdflg = 1;
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
		*NZ = *NZ + 1;
		str = csi;
		csi =-csr;
		csr = str;
		if(i==1) continue; // GO TO 80
		if((YR[i-2]==CZEROR) && (YI[i-2]==CZEROI)) continue; // GO TO 80
		YR[i-2] = CZEROR;
		YI[i-2] = CZEROI;
		*NZ = *NZ + 1;
	} //CONTINUE 80
	i = n;
KT85:
	razr = 1.0/zabs(zrr,zri);
	str = zrr*razr;
	sti = -zri*razr;
	rzr = (str+str)*razr;
	rzi = (sti+sti)*razr;
	ckr = fn*rzr;
	cki = fn*rzi;
	ib = i + 1;
	if(n<ib) goto KT180;
//C-----------------------------------------------------------------------
//C     TEST LAST MEMBER FOR UNDERFLOW AND OVERFLOW. SET SEQUENCE TO ZERO
//C     ON UNDERFLOW.
//C-----------------------------------------------------------------------
	fn = fnu + (double)(n-1);
	ipard = 1;
	if(mr!=0) ipard = 0;
	zunhj(znr, zni, fn, ipard, tol, &phidr, &phidi, &argdr, &argdi, &zet1dr,
	      &zet1di, &zet2dr, &zet2di, &asumdr, &sumdi, &bsumdr, &bsumdi, debug);
	if(kode==1) goto KT90;
	str = zbr + zet2dr;
	sti = zbi + zet2di;
	rast = fn/zabs(str,sti);
	str = str*rast*rast;
	sti = -sti*rast*rast;
	s1r = zet1dr - str;
	s1i = zet1di - sti;
	goto KT100;
KT90:
	s1r = zet1dr - zet2dr;
	s1i = zet1di - zet2di;
KT100:
	rs1 = s1r;
	if(std::abs(rs1)>elim) goto KT105;
	if(std::abs(rs1)<alim) goto KT120;
//C----------------------------------------------------------------------------
//C     REFINE ESTIMATE AND TEST
//C-------------------------------------------------------------------------
	aphi = zabs(phidr,phidi);
	rs1 = rs1+std::log(aphi);
	if(std::abs(rs1)<elim) goto KT120;
KT105:
	if(rs1>0.0) goto KT320;
//C-----------------------------------------------------------------------
//C     FOR ZR.LT.0.0, THE I FUNCTION TO BE ADDED WILL OVERFLOW
//C-----------------------------------------------------------------------
	if(zr<0.0) goto KT320;
	*NZ = n;
	for(i=1; i<=n; i++) { //DO 106
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 106
	return;
KT120:
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	c1r = csrr[kflag-1];
	ascle = bry[kflag-1];
	for(i=ib; i<=n; i++) { //DO 130
		c2r = s2r;
		c2i = s2i;
		s2r = ckr*c2r - cki*c2i + s1r;
		s2i = ckr*c2i + cki*c2r + s1i;
		s1r = c2r;
		s1i = c2i;
		ckr = ckr + rzr;
		cki = cki + rzi;
		c2r = s2r*c1r;
		c2i = s2i*c1r;
		YR[i-1] = c2r;
		YI[i-1] = c2i;
		if(kflag>=3) continue; // GO TO 130
		str = std::abs(c2r);
		sti = std::abs(c2i);
		c2m = std::max(str,sti);
		if(c2m<=ascle) continue; // GO TO 130
		kflag = kflag + 1;
		ascle = bry[kflag-1];
		s1r = s1r*c1r;
		s1i = s1i*c1r;
		s2r = c2r;
		s2i = c2i;
		s1r = s1r*cssr[kflag-1];
		s1i = s1i*cssr[kflag-1];
		s2r = s2r*cssr[kflag-1];
		s2i = s2i*cssr[kflag-1];
		c1r = csrr[kflag-1];
	} //CONTINUE 130
KT180:
	if(mr==0) return;
//C-----------------------------------------------------------------------
//C     ANALYTIC CONTINUATION FOR RE(Z).LT.0.0D0
//C-----------------------------------------------------------------------
	*NZ = 0;
	fmr = (double)mr;
	sgn = -dsign(_PI_,fmr);
//C-----------------------------------------------------------------------
//C     CSPN AND CSGN ARE COEFF OF K AND I FUNCIONS RESP.
//C-----------------------------------------------------------------------
	csgni = sgn;
	if(yy<=0.0) csgni = -csgni;
	ifn = inu + n - 1;
	ang = fnf*sgn;
	cspnr = std::cos(ang);
	cspni = std::sin(ang);
	if((ifn&1)==0) goto KT190;
	cspnr = -cspnr;
	cspni = -cspni;
KT190:
//C-----------------------------------------------------------------------
//C     CS=COEFF OF THE J FUNCTION TO GET THE I FUNCTION. I(FNU,Z) IS
//C     COMPUTED FROM EXP(I*FNU*HPI)*J(FNU,-I*Z) WHERE Z IS IN THE FIRST
//C     QUADRANT. FOURTH QUADRANT VALUES (YY.LE.0.0E0) ARE COMPUTED BY
//C     CONJUGATION SINCE THE I FUNCTION IS REAL ON THE POSITIVE REAL AXIS
//C-----------------------------------------------------------------------
	csr = sar*csgni;
	csi = car*csgni;
	in = (ifn&3) + 1;
	c2r = cipr[in-1];
	c2i = cipi[in-1];
	str = csr*c2r + csi*c2i;
	csi = -csr*c2i + csi*c2r;
	csr = str;
	asc = bry[0];
	iuf = 0;
	kk = n;
	kdflg = 1;
	ib = ib - 1;
	ic = ib - 1;
	for(k=1; k<=n; k++) { //DO 290
		fn = fnu + (double)(kk-1);
//C-----------------------------------------------------------------------
//C     LOGIC TO SORT OUT CASES WHOSE PARAMETERS WERE SET FOR THE K
//C     FUNCTION ABOVE
//C-----------------------------------------------------------------------
		if(n>2) goto KT175;
KT172:
		phidr = phir[j-1];
		phidi = phii[j-1];
		argdr = argr[j-1];
		argdi = argi[j-1];
		zet1dr = zeta1r[j-1];
		zet1di = zeta1i[j-1];
		zet2dr = zeta2r[j-1];
		zet2di = zeta2i[j-1];
		asumdr = asumr[j-1];
		sumdi = asumi[j-1];
		bsumdr = bsumr[j-1];
		bsumdi = bsumi[j-1];
		j = 3 - j;
		goto KT210;
KT175:
		if((kk==n) && (ib<n)) goto KT210;
		if((kk==ib) || (kk==ic)) goto KT172;
		zunhj(znr, zni, fn, 0, tol, &phidr, &phidi, &argdr, &argdi, &zet1dr, &zet1di,
		      &zet2dr, &zet2di, &asumdr, &sumdi, &bsumdr, &bsumdi, debug);
KT210:
		if(kode==1) goto KT220;
		str = zbr + zet2dr;
		sti = zbi + zet2di;
		rast = fn/zabs(str,sti);
		str = str*rast*rast;
		sti = -sti*rast*rast;
		s1r = -zet1dr + str;
		s1i = -zet1di + sti;
		goto KT230;
KT220:
		s1r = -zet1dr + zet2dr;
		s1i = -zet1di + zet2di;
KT230:
//C-----------------------------------------------------------------------
//C     TEST FOR UNDERFLOW AND OVERFLOW
//C-----------------------------------------------------------------------
		rs1 = s1r;
		if(std::abs(rs1)>elim) goto KT280;
		if(kdflg==1) iflag = 2;
		if(std::abs(rs1)<alim) goto KT240;
//C-----------------------------------------------------------------------
//C     REFINE  TEST AND SCALE
//C-----------------------------------------------------------------------
		aphi = zabs(phidr,phidi);
		aarg = zabs(argdr,argdi);
		rs1 = rs1 + std::log(aphi) - 0.25*std::log(aarg) - AIC;
		if(std::abs(rs1)>elim) goto KT280;
		if(kdflg==1) iflag = 1;
		if(rs1<0.0) goto KT240;
		if(kdflg==1) iflag = 3;
KT240:
		zairy(argdr, argdi, 0, 2, &air, &aii, &nai, &idum, debug);
		zairy(argdr, argdi, 1, 2, &dair, &daii, &ndai, &idum, debug);
		str = dair*bsumdr - daii*bsumdi;
		sti = dair*bsumdi + daii*bsumdr;
		str = str + (air*asumdr-aii*sumdi);
		sti = sti + (air*sumdi+aii*asumdr);
		ptr = str*phidr - sti*phidi;
		pti = str*phidi + sti*phidr;
		s2r = ptr*csr - pti*csi;
		s2i = ptr*csi + pti*csr;
		str = std::exp(s1r)*cssr[iflag-1];
		s1r = str*std::cos(s1i);
		s1i = str*std::sin(s1i);
		str = s2r*s1r - s2i*s1i;
		s2i = s2r*s1i + s2i*s1r;
		s2r = str;
		if(iflag!=1) goto KT250;
		zuchk(s2r, s2i, &nw, bry[0], tol, debug);
		if(nw==0) goto KT250;
		s2r = CZEROR;
		s2i = CZEROI;
KT250:
		if(yy<=0.0) s2i = -s2i;
		cyr[kdflg-1] = s2r;
		cyi[kdflg-1] = s2i;
		c2r = s2r;
		c2i = s2i;
		s2r = s2r*csrr[iflag-1];
		s2i = s2i*csrr[iflag-1];
//C-----------------------------------------------------------------------
//C     ADD I AND K FUNCTIONS, K SEQUENCE IN Y(I), I=1,N
//C-----------------------------------------------------------------------
		s1r = YR[kk-1];
		s1i = YI[kk-1];
		if(kode==1) goto KT270;
		zs1s2(zrr, zri, &s1r, &s1i, &s2r, &s2i, &nw, asc, alim, &iuf, debug);
		*NZ = *NZ + nw;
KT270:
		YR[kk-1] = s1r*cspnr - s1i*cspni + s2r;
		YI[kk-1] = s1r*cspni + s1i*cspnr + s2i;
		kk = kk - 1;
		cspnr = -cspnr;
		cspni = -cspni;
		str = csi;
		csi = -csr;
		csr = str;
		if(c2r!=0.0 || c2i!=0.0) goto KT255;
		kdflg = 1;
		continue; // GO TO 290
KT255:
		if(kdflg==2) goto KT295;
		kdflg = 2;
		continue; // GO TO 290
KT280:
		if(rs1>0.0) goto KT320;
		s2r = CZEROR;
		s2i = CZEROI;
		goto KT250;
	} //CONTINUE 290
	k = n;
KT295:
	il = n - k;
	if(il==0) return;
//C-----------------------------------------------------------------------
//C     RECUR BACKWARD FOR REMAINDER OF I SEQUENCE AND ADD IN THE
//C     K FUNCTIONS, SCALING THE I SEQUENCE DURING RECURRENCE TO KEEP
//C     INTERMEDIATE ARITHMETIC ON SCALE NEAR EXPONENT EXTREMES.
//C-----------------------------------------------------------------------
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	csr = csrr[iflag-1];
	ascle = bry[iflag-1];
	fn = (double)(inu+il);
	for(i=1; i<=il; i++) { //DO 310
		c2r = s2r;
		c2i = s2i;
		s2r = s1r + (fn+fnf)*(rzr*c2r-rzi*c2i);
		s2i = s1i + (fn+fnf)*(rzr*c2i+rzi*c2r);
		s1r = c2r;
		s1i = c2i;
		fn = fn - 1.0;
		c2r = s2r*csr;
		c2i = s2i*csr;
		ckr = c2r;
		cki = c2i;
		c1r = YR[kk-1];
		c1i = YI[kk-1];
		if(kode==1) goto KT300;
		zs1s2(zrr, zri, &c1r, &c1i, &c2r, &c2i, &nw, asc, alim, &iuf, debug);
		*NZ = *NZ + nw;
KT300:
		YR[kk-1] = c1r*cspnr - c1i*cspni + c2r;
		YI[kk-1] = c1r*cspni + c1i*cspnr + c2i;
		kk = kk - 1;
		cspnr = -cspnr;
		cspni = -cspni;
		if(iflag>=3) continue; // GO TO 310
		c2r = std::abs(ckr);
		c2i = std::abs(cki);
		c2m = std::max(c2r,c2i);
		if(c2m<=ascle) continue; // GO TO 310
		iflag = iflag + 1;
		ascle = bry[iflag-1];
		s1r = s1r*csr;
		s1i = s1i*csr;
		s2r = ckr;
		s2i = cki;
		s1r = s1r*cssr[iflag-1];
		s1i = s1i*cssr[iflag-1];
		s2r = s2r*cssr[iflag-1];
		s2i = s2i*cssr[iflag-1];
		csr = csrr[iflag-1];
	} //CONTINE 310
	return;
KT320:
	*NZ = -1;
	return;
}
//use: cunk1, cunk2
void zbunk(double zr, double zi, double fnu, int kode, int mr, int n, double *YR, double *YI, int *NZ, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbunk\n");
	double ax, ay;

	*NZ = 0;
	ax = std::abs(zr)*RT3; //1.7321;
	ay = std::abs(zi);
	if(ay>ax) goto NK10;
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR K(FNU,Z) FOR LARGE FNU APPLIED IN
//C     -PI/3.LE.ARG(Z).LE.PI/3
//C-----------------------------------------------------------------------
	zunk1(zr, zi, fnu, kode, mr, n, YR, YI, NZ, tol, elim, alim, debug);
	goto NK20;
NK10:
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR H(2,FNU,Z*EXP(M*HPI)) FOR LARGE FNU
//C     APPLIED IN PI/3.LT.ABS(ARG(Z)).LE.PI/2 WHERE M=+I OR -I
//C     AND HPI=PI/2
//C-----------------------------------------------------------------------
	zunk2(zr, zi, fnu, kode, mr, n, YR, YI, NZ, tol, elim, alim, debug);
NK20:
	return;
}




//****************************************************
//**** Bessel I function                          ****
//**** modified Bessel function of the first kind ****
//****************************************************

//use: cuchk, cunik, cuoik
void zuni1(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, int *NLAST, double fnul, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zuni1 with n=%d\n",n);
	double aphi, ascle, crsc, cscl, c1r, c2i, c2m, c2r, fn, phii, phir, rast, rs1, rzi, rzr, \
	       sti, str, sumi, sumr, s1i, s1r, s2i, s2r, zeta1i, zeta1r, zeta2i, zeta2r;
	double bry[3], csrr[3], cssr[3], cworki[16], cworkr[16], cyi[2], cyr[2];
	int    i, iflag, init, k, m, nd, nn, nuf, nw;

	*NZ = 0;
	nd = n;
	*NLAST = 0;
//C-----------------------------------------------------------------------
//C     COMPUTED VALUES WITH EXPONENTS BETWEEN ALIM AND ELIM IN MAG-
//C     NITUDE ARE SCALED TO KEEP INTERMEDIATE ARITHMETIC ON SCALE,
//C     EXP(ALIM)=EXP(ELIM)*TOL
//C-----------------------------------------------------------------------
	cscl = 1.0/tol;
	crsc = tol;
	cssr[0] = cscl;
	cssr[1] = CONER;
	cssr[2] = crsc;
	csrr[0] = crsc;
	csrr[1] = CONER;
	csrr[2] = cscl;
	bry[0] = 1000.0*D1MACH[0]/tol;
//C-----------------------------------------------------------------------
//C     CHECK FOR UNDERFLOW AND OVERFLOW ON FIRST MEMBER
//C-----------------------------------------------------------------------
	fn = std::max(fnu,1.0);
	init = 0;
	zunik(zr, zi, fn, 1, 1, tol, &init, &phir, &phii, &zeta1r, &zeta1i, \
	      &zeta2r, &zeta2i, &sumr, &sumi, cworkr, cworki, debug);
	if(kode==1) goto IO10;
	str = zr + zeta2r;
	sti = zi + zeta2i;
	rast = fn/zabs(str,sti);
	str = str*rast*rast;
	sti = -sti*rast*rast;
	s1r = -zeta1r + str;
	s1i = -zeta1i + sti;
	goto IO20;
IO10:
	s1r = -zeta1r + zeta2r;
	s1i = -zeta1i + zeta2i;
IO20:
	rs1 = s1r;
	if(std::abs(rs1)>elim) goto IO130;
IO30:
	nn = std::min(2,nd);
	for(i=1; i<=nn; i++) { //DO 80
		fn = fnu + (double)(nd-i);
		init = 0;
		zunik(zr, zi, fn, 1, 0, tol, &init, &phir, &phii, &zeta1r, &zeta1i, \
		      &zeta2r, &zeta2i, &sumr, &sumi, cworkr, cworki, debug);
		if(kode==1) goto IO40;
		str = zr + zeta2r;
		sti = zi + zeta2i;
		rast = fn/zabs(str,sti);
		str = str*rast*rast;
		sti = -sti*rast*rast;
		s1r = -zeta1r + str;
		s1i = -zeta1i + sti + zi;
		goto IO50;
IO40:
		s1r = -zeta1r + zeta2r;
		s1i = -zeta1i + zeta2i;
IO50:
//C-----------------------------------------------------------------------
//C     TEST FOR UNDERFLOW AND OVERFLOW
//C-----------------------------------------------------------------------
		rs1 = s1r;
		if(std::abs(rs1)>elim) goto IO110;
		if(i==1) iflag = 2;
		if(std::abs(rs1)<alim) goto IO60;
//C-----------------------------------------------------------------------
//C     REFINE  TEST AND SCALE
//C-----------------------------------------------------------------------
		aphi = zabs(phir,phii);
		rs1 = rs1 + std::log(aphi);
		if(std::abs(rs1)>elim) goto IO110;
		if(i==1) iflag = 1;
		if(rs1<0.0) goto IO60;
		if(i==1) iflag = 3;
IO60:
//C-----------------------------------------------------------------------
//C     SCALE S1 IF CABS(S1).LT.ASCLE
//C-----------------------------------------------------------------------
		s2r = phir*sumr - phii*sumi;
		s2i = phir*sumi + phii*sumr;
		str = std::exp(s1r)*cssr[iflag-1];
		s1r = str*std::cos(s1i);
		s1i = str*std::sin(s1i);
		str = s2r*s1r - s2i*s1i;
		s2i = s2r*s1i + s2i*s1r;
		s2r = str;
		if(iflag!=1) goto IO70;
		zuchk(s2r, s2i, &nw, bry[0], tol, debug);
		if(nw!=0) goto IO110;
IO70:
		cyr[i-1] = s2r;
		cyi[i-1] = s2i;
		m = nd - i + 1;
		YR[m-1] = s2r*csrr[iflag-1];
		YI[m-1] = s2i*csrr[iflag-1];
	} //CONTINUE 80
	if(nd<=2) goto IO100;
	rast = 1.0/zabs(zr,zi);
	str = zr*rast;
	sti = -zi*rast;
	rzr = (str+str)*rast;
	rzi = (sti+sti)*rast;
	bry[1] = 1.0/bry[0];
	bry[2] = D1MACH[1];
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	c1r = csrr[iflag-1];
	ascle = bry[iflag-1];
	k = nd - 2;
	fn = (double)k;
	for(i=3; i<=nd; i++) { //DO 90
		c2r = s2r;
		c2i = s2i;
		s2r = s1r + (fnu+fn)*(rzr*c2r-rzi*c2i);
		s2i = s1i + (fnu+fn)*(rzr*c2i+rzi*c2r);
		s1r = c2r;
		s1i = c2i;
		c2r = s2r*c1r;
		c2i = s2i*c1r;
		YR[k-1] = c2r;
		YI[k-1] = c2i;
		k = k - 1;
		fn = fn - 1.0;
		if(iflag>=3) continue; // GO TO 90
		str = std::abs(c2r);
		sti = std::abs(c2i);
		c2m = std::max(str,sti);
		if(c2m<=ascle) continue; // GO TO 90
		iflag = iflag + 1;
		ascle = bry[iflag-1];
		s1r = s1r*c1r;
		s1i = s1i*c1r;
		s2r = c2r;
		s2i = c2i;
		s1r = s1r*cssr[iflag-1];
		s1i = s1i*cssr[iflag-1];
		s2r = s2r*cssr[iflag-1];
		s2i = s2i*cssr[iflag-1];
		c1r = csrr[iflag-1];
	} //CONTINUE 90
IO100:
	return;
//C-----------------------------------------------------------------------
//C     SET UNDERFLOW AND UPDATE PARAMETERS
//C-----------------------------------------------------------------------
IO110:
	if(rs1>0.0) goto IO120;
	YR[nd-1] = CZEROR;
	YI[nd-1] = CZEROI;
	*NZ = *NZ + 1;
	nd = nd - 1;
	if(nd==0) goto IO100;
	zuoik(zr, zi, fnu, kode, 1, nd, YR, YI, &nuf, tol, elim, alim, debug);
	if(nuf<0) goto IO120;
	nd = nd - nuf;
	*NZ = *NZ + nuf;
	if(nd==0) goto IO100;
	fn = fnu + (double)(nd-1);
	if(fn>=fnul) goto IO30;
	*NLAST = nd;
	return;
IO120:
	*NZ = -1;
	return;
IO130:
	if(rs1>0.0) goto IO120;
	*NZ = n;
	for(i=1; i<=n; i++) { //DO 140
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 140
	return;
}
//use: cairy, cuchk, cunhj, cuoik
void zuni2(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, int *NLAST, double fnul, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zuni2\n");
	double aarg, aii, air, ang, aphi, argi, argr, ascle, asumi, asumr, bsumi, bsumr, car, cidi, crsc, cscl, \
	       c1r, c2i, c2m, c2r, daii, dair, fn, phii, phir, rast, raz, rs1, rzi, rzr, sar, sti, str, \
	       s1i, s1r, s2i, s2r, zbi, zbr, zeta1i, zeta1r, zeta2i, zeta2r, zni, znr;
	double bry[3], cipi[4], cipr[4], csrr[3], cssr[3], cyi[2], cyr[2];
	int    i,idum, iflag, in, inu, j, k, nai, nd, ndai, nn, nuf, nw;

	cipr[0] =  1.0; cipi[0] =  0.0;
	cipr[1] =  0.0; cipi[1] =  1.0;
	cipr[2] = -1.0; cipi[2] =  0.0;
	cipr[3] =  0.0; cipi[3] = -1.0;

	*NZ = 0;
	nd = n;
	*NLAST = 0;
//C-----------------------------------------------------------------------
//C     COMPUTED VALUES WITH EXPONENTS BETWEEN ALIM AND ELIM IN MAG-
//C     NITUDE ARE SCALED TO KEEP INTERMEDIATE ARITHMETIC ON SCALE,
//C     EXP(ALIM)=EXP(ELIM)*TOL
//C-----------------------------------------------------------------------
	cscl = 1.0/tol;
	crsc = tol;
	cssr[0] = cscl;
	cssr[1] = CONER;
	cssr[2] = crsc;
	csrr[0] = crsc;
	csrr[1] = CONER;
	csrr[2] = cscl;
	bry[0] = 1000.0*D1MACH[0]/tol;
//C-----------------------------------------------------------------------
//C     ZN IS IN THE RIGHT HALF PLANE AFTER ROTATION BY CI OR -CI
//C-----------------------------------------------------------------------
	znr = zi;
	zni = -zr;
	zbr = zr;
	zbi = zi;
	cidi = -CONER;
	inu = (int)fnu;
	ang = HPI*(fnu-(double)inu);
	c2r = std::cos(ang);
	c2i = std::sin(ang);
	car = c2r;
	sar = c2i;
	in = inu + n - 1;
	in = (in&3) + 1;
	str = c2r*cipr[in-1] - c2i*cipi[in-1];
	c2i = c2r*cipi[in-1] + c2i*cipr[in-1];
	c2r = str;
	if(zi>0.0) goto IT10;
	znr = -znr;
	zbi = -zbi;
	cidi = -cidi;
	c2i = -c2i;
IT10:
//C-----------------------------------------------------------------------
//C     CHECK FOR UNDERFLOW AND OVERFLOW ON FIRST MEMBER
//C-----------------------------------------------------------------------
	fn = std::max(fnu,1.0);
	zunhj(znr, zni, fn, 1, tol, &phir, &phii, &argr, &argi, &zeta1r, &zeta1i,
	      &zeta2r, &zeta2i, &asumr, &asumi, &bsumr, &bsumi, debug);
	if(kode==1) goto IT20;
	str = zbr + zeta2r;
	sti = zbi + zeta2i;
	rast = fn/zabs(str,sti);
	str = str*rast*rast;
	sti = -sti*rast*rast;
	s1r = -zeta1r + str;
	s1i = -zeta1i + sti;
	goto IT30;
IT20:
	s1r = -zeta1r + zeta2r;
	s1i = -zeta1i + zeta2i;
IT30:
	rs1 = s1r;
	if(std::abs(rs1)>elim) goto IT150;
IT40:
	nn = std::min(2,nd);
	for(i=1; i<=nn; i++) { //DO 90
		fn = fnu + (double)(nd-i);
		zunhj(znr, zni, fn, 0, tol, &phir, &phii, &argr, &argi, &zeta1r, &zeta1i, \
		      &zeta2r, &zeta2i, &asumr, &asumi, &bsumr, &bsumi, debug);
		if(kode==1) goto IT50;
		str = zbr + zeta2r;
		sti = zbi + zeta2i;
		rast = fn/zabs(str,sti);
		str = str*rast*rast;
		sti = -sti*rast*rast;
		s1r = -zeta1r + str;
		s1i = -zeta1i + sti + std::abs(zi);
		goto IT60;
IT50:
		s1r = -zeta1r + zeta2r;
		s1i = -zeta1i + zeta2i;
IT60:
//C-----------------------------------------------------------------------
//C     TEST FOR UNDERFLOW AND OVERFLOW
//C-----------------------------------------------------------------------
		rs1 = s1r;
		if(std::abs(rs1)>elim) goto IT120;
		if(i==1) iflag = 2;
		if(std::abs(rs1)<alim) goto IT70;
//C-----------------------------------------------------------------------
//C     REFINE  TEST AND SCALE
//C-----------------------------------------------------------------------
//C-----------------------------------------------------------------------
		aphi = zabs(phir,phii);
		aarg = zabs(argr,argi);
		rs1 = rs1 + std::log(aphi) - 0.25*std::log(aarg) - AIC;
		if(std::abs(rs1)>elim) goto IT120;
		if(i==1) iflag = 1;
		if(rs1<0.0) goto IT70;
		if(i==1) iflag = 3;
IT70:
//C-----------------------------------------------------------------------
//C     SCALE S1 TO KEEP INTERMEDIATE ARITHMETIC ON SCALE NEAR
//C     EXPONENT EXTREMES
//C-----------------------------------------------------------------------
		zairy(argr, argi, 0, 2, &air, &aii, &nai, &idum, debug);
		zairy(argr, argi, 1, 2, &dair, &daii, &ndai, &idum, debug);
		str = dair*bsumr - daii*bsumi;
		sti = dair*bsumi + daii*bsumr;
		str = str + (air*asumr-aii*asumi);
		sti = sti + (air*asumi+aii*asumr);
		s2r = phir*str - phii*sti;
		s2i = phir*sti + phii*str;
		str = std::exp(s1r)*cssr[iflag-1];
		s1r = str*std::cos(s1i);
		s1i = str*std::sin(s1i);
		str = s2r*s1r - s2i*s1i;
		s2i = s2r*s1i + s2i*s1r;
		s2r = str;
		if(iflag!=1) goto IT80;
		zuchk(s2r, s2i, &nw, bry[0], tol, debug);
		if(nw!=0) goto IT120;
IT80:
		if(zi<=0.0) s2i = -s2i;
		str = s2r*c2r - s2i*c2i;
		s2i = s2r*c2i + s2i*c2r;
		s2r = str;
		cyr[i-1] = s2r;
		cyi[i-1] = s2i;
		j = nd - i + 1;
		YR[j-1] = s2r*csrr[iflag-1];
		YI[j-1] = s2i*csrr[iflag-1];
		str = -c2i*cidi;
		c2i = c2r*cidi;
		c2r = str;
	} //CONTINUE 90
	if(nd<=2) goto IT110;
	raz = 1.0/zabs(zr,zi);
	str = zr*raz;
	sti = -zi*raz;
	rzr = (str+str)*raz;
	rzi = (sti+sti)*raz;
	bry[1]= 1.0/bry[0];
	bry[2] = D1MACH[1];
	s1r = cyr[0];
	s1i = cyi[0];
	s2r = cyr[1];
	s2i = cyi[1];
	c1r = csrr[iflag-1];
	ascle = bry[iflag-1];
	k = nd - 2;
	fn = (double)k;
	for(i=3; i<=nd; i++) { //DO 100
		c2r = s2r;
		c2i = s2i;
		s2r = s1r + (fnu+fn)*(rzr*c2r-rzi*c2i);
		s2i = s1i + (fnu+fn)*(rzr*c2i+rzi*c2r);
		s1r = c2r;
		s1i = c2i;
		c2r = s2r*c1r;
		c2i = s2i*c1r;
		YR[k-1] = c2r;
		YI[k-1] = c2i;
		k = k - 1;
		fn = fn - 1.0;
		if(iflag>=3) continue; // GO TO 100
		str = std::abs(c2r);
		sti = std::abs(c2i);
		c2m = std::max(str,sti);
		if(c2m<=ascle) continue; // GO TO 100
		iflag = iflag + 1;
		ascle = bry[iflag-1];
		s1r = s1r*c1r;
		s1i = s1i*c1r;
		s2r = c2r;
		s2i = c2i;
		s1r = s1r*cssr[iflag-1];
		s1i = s1i*cssr[iflag-1];
		s2r = s2r*cssr[iflag-1];
		s2i = s2i*cssr[iflag-1];
		c1r = csrr[iflag-1];
	} //CONTINUE 100
IT110:
	return;
IT120:
	if(rs1>0.0) goto IT140;
//C-----------------------------------------------------------------------
//C     SET UNDERFLOW AND UPDATE PARAMETERS
//C-----------------------------------------------------------------------
	YR[nd-1] = CZEROR;
	YI[nd-1] = CZEROI;
	*NZ = *NZ + 1;
	nd = nd - 1;
	if(nd==0) goto IT110;
	zuoik(zr, zi, fnu, kode, 1, nd, YR, YI, &nuf, tol, elim, alim, debug);
	if(nuf<0) goto IT140;
	nd = nd - nuf;
	*NZ = *NZ + nuf;
	if(nd==0) goto IT110;
	fn = fnu + (double)(nd-1);
	if(fn<fnul) goto IT130;
//C      FN = CIDI
//C      J = NUF + 1
//C      K = MOD(J,4) + 1
//C      S1R = CIPR(K)
//C      S1I = CIPI(K)
//C      IF (FN.LT.0.0D0) S1I = -S1I
//C      STR = C2R*S1R - C2I*S1I
//C      C2I = C2R*S1I + C2I*S1R
//C      C2R = STR
	in = inu + nd - 1;
	in =(in&3) + 1;
	c2r = car*cipr[in-1] - sar*cipi[in-1];
	c2i = car*cipi[in-1] + sar*cipr[in-1];
	if(zi<=0.0) c2i = -c2i;
	goto IT40;
IT130:
	*NLAST = nd;
	return;
IT140:
	*NZ = -1;
	return;
IT150:
	if(rs1>0.0) goto IT140;
	*NZ = n;
	for(i=1; i<=n; i++) { //DO 160
		YR[i-1] = CZEROR;
		YI[i-1] = CZEROI;
	} //CONTINUE 160
	return;
}
//use: cuni1, cuni2
void zbuni(double zr, double zi, double fnu, int kode, int n, double *YR, double *YI, int *NZ, int nui, int *NLAST, double fnul, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbuni\n");
	double ascle, ax, ay, csclr, cscrr, c1i, c1m, c1r, dfnu, fnui, gnu, raz, rzi, rzr, \
	       sti, str, s1i, s1r, s2i, s2r;
	double bry[3], cyi[2], cyr[2];
	int    i, iflag, iform, k, nl, nw;

	*NZ = 0;
	ax = std::abs(zr)*RT3; //1.7321;
	ay = std::abs(zi);
	iform = 1;
	if(ay>ax) iform = 2;
	if(nui==0) goto NI60;
	fnui = (double)nui;
	dfnu = fnu + (double)(n-1);
	gnu = dfnu + fnui;
	if(iform==2) goto NI10;
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR I(FNU,Z) FOR LARGE FNU APPLIED IN
//C     -PI/3.LE.ARG(Z).LE.PI/3
//C-----------------------------------------------------------------------
	zuni1(zr, zi, gnu, kode, 2, cyr, cyi, &nw, NLAST, fnul, tol, elim, alim, debug);
	goto NI20;
NI10:
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR J(FNU,Z*EXP(M*HPI)) FOR LARGE FNU
//C     APPLIED IN PI/3.LT.ABS(ARG(Z)).LE.PI/2 WHERE M=+I OR -I
//C     AND HPI=PI/2
//C-----------------------------------------------------------------------
	zuni2(zr, zi, gnu, kode, 2, cyr, cyi, &nw, NLAST, fnul, tol, elim, alim, debug);
NI20:
	if(nw<0) goto NI50;
	if(nw!=0) goto NI90;
	str = zabs(cyr[0],cyi[0]);
//C----------------------------------------------------------------------
//C     SCALE BACKWARD RECURRENCE, BRY(3) IS DEFINED BUT NEVER USED
//C----------------------------------------------------------------------
	bry[0]=1000.0*D1MACH[0]/tol;
	bry[1] = 1.0/bry[0];
	bry[2] = bry[1];
	iflag = 2;
	ascle = bry[1];
	csclr = 1.0;
	if(str>bry[0]) goto NI21;
	iflag = 1;
	ascle = bry[0];
	csclr = 1.0/tol;
	goto NI25;
NI21:
	if(str<bry[1]) goto NI25;
	iflag = 3;
	ascle=bry[2];
	csclr = tol;
NI25:
	cscrr = 1.0/csclr;
	s1r = cyr[1]*csclr;
	s1i = cyi[1]*csclr;
	s2r = cyr[0]*csclr;
	s2i = cyi[0]*csclr;
	raz = 1.0/zabs(zr,zi);
	str = zr*raz;
	sti = -zi*raz;
	rzr = (str+str)*raz;
	rzi = (sti+sti)*raz;
	for(i=1; i<=nui; i++) { //DO 30
		str = s2r;
		sti = s2i;
		s2r = (dfnu+fnui)*(rzr*str-rzi*sti) + s1r;
		s2i = (dfnu+fnui)*(rzr*sti+rzi*str) + s1i;
		s1r = str;
		s1i = sti;
		fnui = fnui - 1.0;
		if(iflag>=3) continue; // GO TO 30
		str = s2r*cscrr;
		sti = s2i*cscrr;
		c1r = std::abs(str);
		c1i = std::abs(sti);
		c1m = std::max(c1r,c1i);
		if(c1m<=ascle) continue; // GO TO 30
		iflag = iflag+1;
		ascle = bry[iflag-1];
		s1r = s1r*cscrr;
		s1i = s1i*cscrr;
		s2r = str;
		s2i = sti;
		csclr = csclr*tol;
		cscrr = 1.0/csclr;
		s1r = s1r*csclr;
		s1i = s1i*csclr;
		s2r = s2r*csclr;
		s2i = s2i*csclr;
	} //CONTINUE 30
	YR[n-1] = s2r*cscrr;
	YI[n-1] = s2i*cscrr;
	if(n==1) return;
	nl = n - 1;
	fnui = (double)nl;
	k = nl;
	for(i=1; i<=nl; i++) { //DO 40
		str = s2r;
		sti = s2i;
		s2r = (fnu+fnui)*(rzr*str-rzi*sti) + s1r;
		s2i = (fnu+fnui)*(rzr*sti+rzi*str) + s1i;
		s1r = str;
		s1i = sti;
		str = s2r*cscrr;
		sti = s2i*cscrr;
		YR[k-1] = str;
		YI[k-1] = sti;
		fnui = fnui - 1.0;
		k = k - 1;
		if(iflag>=3) continue; // GO TO 40
		c1r = std::abs(str);
		c1i = std::abs(sti);
		c1m = std::max(c1r,c1i);
		if(c1m<=ascle) continue; // GO TO 40
		iflag = iflag+1;
		ascle = bry[iflag-1];
		s1r = s1r*cscrr;
		s1i = s1i*cscrr;
		s2r = str;
		s2i = sti;
		csclr = csclr*tol;
		cscrr = 1.0/csclr;
		s1r = s1r*csclr;
		s1i = s1i*csclr;
		s2r = s2r*csclr;
		s2i = s2i*csclr;
	} //CONTINUE 40
	return;
NI50:
	*NZ = -1;
	if(nw==(-2)) *NZ = -2;
	return;
NI60:
	if(iform==2) goto NI70;
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR I(FNU,Z) FOR LARGE FNU APPLIED IN
//C     -PI/3.LE.ARG(Z).LE.PI/3
//C-----------------------------------------------------------------------
	zuni1(zr, zi, fnu, kode, n, YR, YI, &nw, NLAST, fnul, tol, elim, alim, debug);
	goto NI80;
NI70:
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR J(FNU,Z*EXP(M*HPI)) FOR LARGE FNU
//C     APPLIED IN PI/3.LT.ABS(ARG(Z)).LE.PI/2 WHERE M=+I OR -I
//C     AND HPI=PI/2
//C-----------------------------------------------------------------------
	zuni2(zr, zi, fnu, kode, n, YR, YI, &nw, NLAST, fnul, tol, elim, alim, debug);
NI80:
	if(nw<0) goto NI50;
	*NZ = nw;
	return;
NI90:
	*NLAST = n;
	return;
}
//use: casyi, cbuni, cmlri, cseri, cuoik, cwrsk
void zbinu(double zr, double zi, double fnu, int kode, int n, double *CYR, double *CYI, int *NZ, double rl, double fnul, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbinu\n");
	double az, dfnu;
	double cwi[2], cwr[2];
	int    i, inw, nlast, nn, nui, nw;

	*NZ = 0;
	az = zabs(zr,zi);
	nn = n;
	dfnu = fnu + (double)(n-1);
	if(az<=2.0) goto BI10;
	if(az*az*0.25>dfnu+1.0) goto BI20;
BI10:
//C-----------------------------------------------------------------------
//C     POWER SERIES
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: power series\n");
	zseri(zr, zi, fnu, kode, nn, CYR, CYI, &nw, tol, elim, alim, debug);
	inw = std::abs(nw);
	*NZ = *NZ + inw;
	nn = nn - inw;
	if(nn==0) return;
	if(nw>=0) goto BI120;
	dfnu = fnu + (double)(nn-1);
BI20:
	if(az<rl) goto BI40;
	if(dfnu<=1.0) goto BI30;
	if(az+az<dfnu*dfnu) goto BI50;
//C-----------------------------------------------------------------------
//C     ASYMPTOTIC EXPANSION FOR LARGE Z
//C-----------------------------------------------------------------------
BI30:
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: asymptotic expansion\n");
	zasyi(zr, zi, fnu, kode, nn, CYR, CYI, &nw, rl, tol, elim, alim, debug);
	if(nw<0) goto BI130;
	goto BI120;
BI40:
	if(dfnu<=1.0) goto BI70;
BI50:
//C-----------------------------------------------------------------------
//C     OVERFLOW AND UNDERFLOW TEST ON I SEQUENCE FOR MILLER ALGORITHM
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: over-/underflow tests on I sequence for Miller algorithm\n");
	zuoik(zr, zi, fnu, kode, 1, nn, CYR, CYI, &nw, tol, elim, alim, debug);
	if(nw<0) goto BI130;
	*NZ = *NZ + nw;
	nn = nn - nw;
	if(nn==0) return;
	dfnu = fnu + (double)(nn-1);
	if(dfnu>fnul) goto BI110;
	if(az>fnul) goto BI110;
BI60:
	if(az>rl) goto BI80;
BI70:
//C-----------------------------------------------------------------------
//C     MILLER ALGORITHM NORMALIZED BY THE SERIES
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: Miller algorithm\n");
	zmlri(zr, zi, fnu, kode, nn, CYR, CYI, &nw, tol, debug);
	if(nw<0) goto BI130;
	goto BI120;
BI80:
//C-----------------------------------------------------------------------
//C     MILLER ALGORITHM NORMALIZED BY THE WRONSKIAN
//C-----------------------------------------------------------------------
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST ON K FUNCTIONS USED IN WRONSKIAN
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: use Miller algorithm normalized by the Wronskian\n");
	zuoik(zr, zi, fnu, kode, 2, 2, cwr, cwi, &nw, tol, elim, alim, debug);
	if(nw>=0) goto BI100;
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: overflow occured, reset all output to zero\n");
	*NZ = nn;
	for(i=1; i<=nn; i++) { //DO 90
		CYR[i-1] = CZEROR;
		CYI[i-1] = CZEROI;
	} //CONTINUE 90
	return;
BI100:
	if(nw>0) goto BI130;
	zwrsk(zr, zi, fnu, kode, nn, CYR, CYI, &nw, cwr, cwi, tol, elim, alim, debug);
	if(nw<0) goto BI130;
	goto BI120;
BI110:
//C-----------------------------------------------------------------------
//C     INCREMENT FNU+NN-1 UP TO FNUL, COMPUTE AND RECUR BACKWARD
//C-----------------------------------------------------------------------
	if(*debug) PySys_WriteStdout("[DEBUG] ZBINU: backward recurrence\n");
	nui = (int)(fnul-dfnu) + 1;
	nui = std::max(nui,0);
	zbuni(zr, zi, fnu, kode, nn, CYR, CYI, &nw, nui, &nlast, fnul, tol, elim, alim, debug);
	if(nw<0) goto BI130;
	*NZ = *NZ + nw;
	if(nlast==0) goto BI120;
	nn = nlast;
	goto BI60;
BI120:
	return;
BI130:
	*NZ = -1;
	if(nw==(-2)) *NZ = -2;
	return;
}




//*******************************************
//**** Hankel function                   ****
//**** Bessel function of the third kind ****
//*******************************************

//use: cbinu, cbknu, cs1s2
void zacon(double zr, double zi, double fnu, int kode, int mr, int n, double *YR, double *YI, int *NZ, double rl, double fnul, double tol, double elim, double alim, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zacon\n");
	double arg, ascle, as2, azn, bscle, cki, ckr, cpn, cscl, cscr, csgni, csgnr, cspni, cspnr, csr, \
	       c1i, c1m, c1r, c2i, c2r, fmr, fn, pti, ptr, razn, rzi, rzr, sc1i, sc1r, sc2i, sc2r, sgn, spn, \
	       sti, str, s1i, s1r, s2i, s2r, yy, zni, znr;
	double bry[3], csrr[3], cssr[3], cyi[2], cyr[2];
	int    i, inu, iuf, kflag, nn, nw;

	//initialize, so the compiler is happy
	sc2r = 0.0;
	sc2i = 0.0;
	//end of extra initialization

	*NZ = 0;
	znr = -zr;
	zni = -zi;
	nn = n;
	zbinu(znr, zni, fnu, kode, nn, YR, YI, &nw, rl, fnul, tol, elim, alim, debug);
	if(nw<0) goto AC90;
//C-----------------------------------------------------------------------
//C     ANALYTIC CONTINUATION TO THE LEFT HALF PLANE FOR THE K FUNCTION
//C-----------------------------------------------------------------------
	nn = std::min(2,n);
	zbknu(znr, zni, fnu, kode, nn, cyr, cyi, &nw, tol, elim, alim, debug);
	if(nw!=0) goto AC90;
	s1r = cyr[0];
	s1i = cyi[0];
	fmr = (double)mr;
	sgn = -dsign(_PI_,fmr);
	csgnr = CZEROR;
	csgni = sgn;
	if(kode==1) goto AC10;
	yy = -zni;
	cpn = std::cos(yy);
	spn = std::sin(yy);
	zmlt(csgnr, csgni, cpn, spn, &csgnr, &csgni);
AC10:
//C-----------------------------------------------------------------------
//C     CALCULATE CSPN=EXP(FNU*PI*I) TO MINIMIZE LOSSES OF SIGNIFICANCE
//C     WHEN FNU IS LARGE
//C-----------------------------------------------------------------------
	inu = (int)fnu;
	arg = (fnu-(double)inu)*sgn;
	cpn = std::cos(arg);
	spn = std::sin(arg);
	cspnr = cpn;
	cspni = spn;
	if((inu&1)==0) goto AC20;
	cspnr = -cspnr;
	cspni = -cspni;
AC20:
	iuf = 0;
	c1r = s1r;
	c1i = s1i;
	c2r = YR[0];
	c2i = YI[0];
	ascle = 1000.0*D1MACH[0]/tol;
	if(kode==1) goto AC30;
	zs1s2(znr, zni, &c1r, &c1i, &c2r, &c2i, &nw, ascle, alim, &iuf, debug);
	*NZ = *NZ + nw;
	sc1r = c1r;
	sc1i = c1i;
AC30:
	zmlt(cspnr, cspni, c1r, c1i, &str, &sti);
	zmlt(csgnr, csgni, c2r, c2i, &ptr, &pti);
	YR[0] = str + ptr;
	YI[0] = sti + pti;
	if(n==1) return;
	cspnr = -cspnr;
	cspni = -cspni;
	s2r = cyr[1];
	s2i = cyi[1];
	c1r = s2r;
	c1i = s2i;
	c2r = YR[1];
	c2i = YI[1];
	if(kode==1) goto AC40;
	zs1s2(znr, zni, &c1r, &c1i, &c2r, &c2i, &nw, ascle, alim, &iuf, debug);
	*NZ = *NZ + nw;
	sc2r = c1r;
	sc2i = c1i;
AC40:
	zmlt(cspnr, cspni, c1r, c1i, &str, &sti);
	zmlt(csgnr, csgni, c2r, c2i, &ptr, &pti);
	YR[1] = str + ptr;
	YI[1] = sti + pti;
	if(n==2) return;
	cspnr = -cspnr;
	cspni = -cspni;
	azn = zabs(znr,zni);
	razn = 1.0/azn;
	str = znr*razn;
	sti = -zni*razn;
	rzr = (str+str)*razn;
	rzi = (sti+sti)*razn;
	fn = fnu + 1.0;
	ckr = fn*rzr;
	cki = fn*rzi;
//C-----------------------------------------------------------------------
//C     SCALE NEAR EXPONENT EXTREMES DURING RECURRENCE ON K FUNCTIONS
//C-----------------------------------------------------------------------
	cscl = 1.0/tol;
	cscr = tol;
	cssr[0] = cscl;
	cssr[1] = CONER;
	cssr[2] = cscr;
	csrr[0] = cscr;
	csrr[1] = CONER;
	csrr[2] = cscl;
	bry[0] = ascle;
	bry[1] = 1.0/ascle;
	bry[2] = D1MACH[1];
	as2 = zabs(s2r,s2i);
	kflag = 2;
	if(as2>bry[0]) goto AC50;
	kflag = 1;
	goto AC60;
AC50:
	if(as2<bry[1]) goto AC60;
	kflag = 3;
AC60:
	bscle = bry[kflag-1];
	s1r = s1r*cssr[kflag-1];
	s1i = s1i*cssr[kflag-1];
	s2r = s2r*cssr[kflag-1];
	s2i = s2i*cssr[kflag-1];
	csr = csrr[kflag-1];
	for(i=3; i<=n; i++) { //DO 80
		str = s2r;
		sti = s2i;
		s2r = ckr*str - cki*sti + s1r;
		s2i = ckr*sti + cki*str + s1i;
		s1r = str;
		s1i = sti;
		c1r = s2r*csr;
		c1i = s2i*csr;
		str = c1r;
		sti = c1i;
		c2r = YR[i-1];
		c2i = YI[i-1];
		if(kode==1) goto AC70;
		if(iuf<0) goto AC70;
		zs1s2(znr, zni, &c1r, &c1i, &c2r, &c2i, &nw, ascle, alim, &iuf, debug);
		*NZ = *NZ + nw;
		sc1r = sc2r;
		sc1i = sc2i;
		sc2r = c1r;
		sc2i = c1i;
		if(iuf!=3) goto AC70;
		iuf = -4;
		s1r = sc1r*cssr[kflag-1];
		s1i = sc1i*cssr[kflag-1];
		s2r = sc2r*cssr[kflag-1];
		s2i = sc2i*cssr[kflag-1];
		str = sc2r;
		sti = sc2i;
AC70:
		ptr = cspnr*c1r - cspni*c1i;
		pti = cspnr*c1i + cspni*c1r;
		YR[i-1] = ptr + csgnr*c2r - csgni*c2i;
		YI[i-1] = pti + csgnr*c2i + csgni*c2r;
		ckr = ckr + rzr;
		cki = cki + rzi;
		cspnr = -cspnr;
		cspni = -cspni;
		if(kflag>=3) continue; // GO TO 80
		ptr = std::abs(c1r);
		pti = std::abs(c1i);
		c1m = std::max(ptr,pti);
		if(c1m<=bscle) continue; // GO TO 80
		kflag = kflag + 1;
		bscle = bry[kflag-1];
		s1r = s1r*csr;
		s1i = s1i*csr;
		s2r = str;
		s2i = sti;
		s1r = s1r*cssr[kflag-1];
		s1i = s1i*cssr[kflag-1];
		s2r = s2r*cssr[kflag-1];
		s2i = s2i*cssr[kflag-1];
		csr = csrr[kflag-1];
	} //CONTINUE 80
	return;
AC90:
	*NZ = -1;
	if(nw==(-2)) *NZ = -2;
	return;
}
//use: cacon, cbknu, cbunk, cuoik
void zbesh(double zr, double zi, double fnu, int kode, int m, int n, double *CYR, double *CYI, int *NZ, int *IERR, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbesh\n");
	double  aa, alim, aln, arg, ascle, atol, az, bb, csgni, csgnr, dig, elim, fmm, fn, fnul, \
	        rhpi, rl, rtol, r1m5, sgn, sti, str, tol, ufl, zni, znr, zti;
	int     i, inu, inuh, ir, k, k1, k2, mm, mr, nn, nuf, nw;

	*IERR = 0;
	*NZ = 0;
	if(zr==0.0 && zi==0.0) *IERR = 1;
	if(fnu<0.0) *IERR = 1;
	if(m<1 || m>2) *IERR = 1;
	if(kode<1 || kode>2) *IERR = 1;
	if(n<1) *IERR = 1;
	if(*IERR!=0) return;
	nn = n;
//C-----------------------------------------------------------------------
//C     SET PARAMETERS RELATED TO MACHINE CONSTANTS.
//C     TOL IS THE APPROXIMATE UNIT ROUNDOFF LIMITED TO 1.0E-18.
//C     ELIM IS THE APPROXIMATE EXPONENTIAL OVER- AND UNDERFLOW LIMIT.
//C     EXP(-ELIM).LT.EXP(-ALIM)=EXP(-ELIM)/TOL    AND
//C     EXP(ELIM).GT.EXP(ALIM)=EXP(ELIM)*TOL       ARE INTERVALS NEAR
//C     UNDERFLOW AND OVERFLOW LIMITS WHERE SCALED ARITHMETIC IS DONE.
//C     RL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC EXPANSION FOR LARGE Z.
//C     DIG = NUMBER OF BASE 10 DIGITS IN TOL = 10**(-DIG).
//C     FNUL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC SERIES FOR LARGE FNU
//C-----------------------------------------------------------------------
	tol = std::max(D1MACH[3],1.0e-18);
	k1 = I1MACH[14];
	k2 = I1MACH[15];
	r1m5 = D1MACH[4];
	k = std::min(std::abs(k1),std::abs(k2));
	elim = LN10*((double)k*r1m5-3.0); //2.303*
	k1 = I1MACH[13] - 1;
	aa = r1m5*(double)k1;
	dig = std::min(aa,18.0);
	aa = aa*LN10; //*2.303
	alim = elim + std::max(-aa,-41.45);
	fnul = 10.0 + 6.0*(dig-3.0);
	rl = 1.2*dig + 3.0;
	fn = fnu + (double)(nn-1);
	mm = 3 - m - m;
	fmm = (double)mm;
	znr = fmm*zi;
	zni = -fmm*zr;
//C-----------------------------------------------------------------------
//C     TEST FOR PROPER RANGE
//C-----------------------------------------------------------------------
	az = zabs(zr,zi);
	aa = 0.5/tol;
	bb=(double)I1MACH[8]*0.5;
	aa = std::min(aa,bb);
	if(az>aa) goto HH260;
	if(fn>aa) goto HH260;
	aa = std::sqrt(aa);
	if(az>aa) *IERR = 3;
	if(fn>aa) *IERR = 3;
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST ON THE LAST MEMBER OF THE SEQUENCE
//C-----------------------------------------------------------------------
	ufl = 1000.0*D1MACH[0];
	if(az<ufl) goto HH230;
	if(fnu>fnul) goto HH90;
	if(fn<=1.0) goto HH70;
	if(fn>2.0) goto HH60;
	if(az>tol) goto HH70;
	arg = 0.5*az;
	aln = -fn*std::log(arg);
	if(aln>elim) goto HH230;
	goto HH70;
HH60:
	zuoik(znr, zni, fnu, kode, 2, nn, CYR, CYI, &nuf, tol, elim, alim, debug);
	if(nuf<0) goto HH230;
	*NZ = *NZ + nuf;
	nn = nn - nuf;
//C-----------------------------------------------------------------------
//C     HERE NN=N OR NN=0 SINCE NUF=0,NN, OR -1 ON RETURN FROM CUOIK
//C     IF NUF=NN, THEN CY(I)=CZERO FOR ALL I
//C-----------------------------------------------------------------------
	if(nn==0) goto HH140;
HH70:
	if((znr<0.0) || (znr==0.0 && zni<0.0 && m==2)) goto HH80;
//C-----------------------------------------------------------------------
//C     RIGHT HALF PLANE COMPUTATION, XN.GE.0. .AND. (XN.NE.0. .OR.
//C     YN.GE.0. .OR. M=1)
//C-----------------------------------------------------------------------
	zbknu(znr, zni, fnu, kode, nn, CYR, CYI, NZ, tol, elim, alim, debug);
	goto HH110;
//C-----------------------------------------------------------------------
//C     LEFT HALF PLANE COMPUTATION
//C-----------------------------------------------------------------------
HH80:
	mr = -mm;
	zacon(znr, zni, fnu, kode, mr, nn, CYR, CYI, &nw, rl, fnul, tol, elim, alim, debug);
	if(nw<0) goto HH240;
	*NZ = nw;
	goto HH110;
HH90:
//C-----------------------------------------------------------------------
//C     UNIFORM ASYMPTOTIC EXPANSIONS FOR FNU.GT.FNUL
//C-----------------------------------------------------------------------
	mr = 0;
	if((znr>=0.0) && (znr!=0.0 || zni>=0.0 || m!=2)) goto HH100;
	mr = -mm;
	if(znr!=0.0 || zni>=0.0) goto HH100;
	znr = -znr;
	zni = -zni;
HH100:
	zbunk(znr, zni, fnu, kode, mr, nn, CYR, CYI, &nw, tol, elim, alim, debug);
	if(nw<0) goto HH240;
	*NZ = *NZ + nw;
HH110:
//C-----------------------------------------------------------------------
//C     H(M,FNU,Z) = -FMM*(I/HPI)*(ZT**FNU)*K(FNU,-Z*ZT)
//C
//C     ZT=EXP(-FMM*HPI*I) = CMPLX(0.0,-FMM), FMM=3-2*M, M=1,2
//C-----------------------------------------------------------------------
	sgn = dsign(HPI,-fmm);
//C-----------------------------------------------------------------------
//C     CALCULATE EXP(FNU*HPI*I) TO MINIMIZE LOSSES OF SIGNIFICANCE
//C     WHEN FNU IS LARGE
//C-----------------------------------------------------------------------
	inu = (int)fnu;
	inuh = inu/2;
	ir = inu - 2*inuh;
	arg = (fnu-(double)(inu-ir))*sgn;
	rhpi = 1.0/sgn;
//C     ZNI = RHPI*DCOS(ARG)
//C     ZNR = -RHPI*DSIN(ARG)
	csgni = rhpi*std::cos(arg);
	csgnr = -rhpi*std::sin(arg);
	if((inuh&1)==0) goto HH120;
//C     ZNR = -ZNR
//C     ZNI = -ZNI
	csgnr = -csgnr;
	csgni = -csgni;
HH120:
	zti = -fmm;
	rtol = 1.0/tol;
	ascle = ufl*rtol;
	for(i=1; i<=nn; i++) { //DO 130
//C       STR = CYR(I)*ZNR - CYI(I)*ZNI
//C       CYI(I) = CYR(I)*ZNI + CYI(I)*ZNR
//C       CYR(I) = STR
//C       STR = -ZNI*ZTI
//C       ZNI = ZNR*ZTI
//C       ZNR = STR
		aa = CYR[i-1];
		bb = CYI[i-1];
		atol = 1.0;
		if(std::max(std::abs(aa),std::abs(bb))>ascle) goto HH135;
		aa = aa*rtol;
		bb = bb*rtol;
		atol = tol;
HH135:
		str = aa*csgnr - bb*csgni;
		sti = aa*csgni + bb*csgnr;
		CYR[i-1] = str*atol;
		CYI[i-1] = sti*atol;
		str = -csgni*zti;
		csgni = csgnr*zti;
		csgnr = str;
	} //CONTINUE 130
	return;
HH140:
	if(znr<0.0) goto HH230;
	return;
HH230:
	*NZ = 0;
	*IERR = 2;
	return;
HH240:
	if(nw==(-1)) goto HH230;
	*NZ = 0;
	*IERR = 5;
	return;
HH260:
	*NZ = 0;
	*IERR = 4;
	return;
}




//*******************************************************
//**** Bessel I and K                                ****
//**** Modified Bessel fct. of the first/second kind ****
//*******************************************************

//use: cbinu
void zbesi(double zr, double zi, double fnu, int kode, int n, double *CYR, double *CYI, int *NZ, int *IERR, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbesi\n");
	double aa, alim, arg, ascle, atol, az, bb, csgni, csgnr, dig, elim, fn, fnul, rl, rtol, r1m5, \
	       sti, str, tol, zni, znr;
	int    i, inu, k, k1, k2, nn;

	*IERR = 0;
	*NZ = 0;
	if(fnu<0.0) *IERR = 1;
	if(kode<1 || kode>2) *IERR = 1;
	if(n<1) *IERR = 1;
	if(*IERR!=0) return;
//C-----------------------------------------------------------------------
//C     SET PARAMETERS RELATED TO MACHINE CONSTANTS.
//C     TOL IS THE APPROXIMATE UNIT ROUNDOFF LIMITED TO 1.0E-18.
//C     ELIM IS THE APPROXIMATE EXPONENTIAL OVER- AND UNDERFLOW LIMIT.
//C     EXP(-ELIM).LT.EXP(-ALIM)=EXP(-ELIM)/TOL    AND
//C     EXP(ELIM).GT.EXP(ALIM)=EXP(ELIM)*TOL       ARE INTERVALS NEAR
//C     UNDERFLOW AND OVERFLOW LIMITS WHERE SCALED ARITHMETIC IS DONE.
//C     RL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC EXPANSION FOR LARGE Z.
//C     DIG = NUMBER OF BASE 10 DIGITS IN TOL = 10**(-DIG).
//C     FNUL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC SERIES FOR LARGE FNU.
//C-----------------------------------------------------------------------
	tol = std::max(D1MACH[3],1.0e-18);
	k1 = I1MACH[14];
	k2 = I1MACH[15];
	r1m5 = D1MACH[4];
	k = std::min(std::abs(k1),std::abs(k2));
	elim = LN10*((double)k*r1m5-3.0); //2.303*
	k1 = I1MACH[13] - 1;
	aa = r1m5*(double)k1;
	dig = std::min(aa,18.0);
	aa = aa*LN10; //*2.303
	alim = elim + std::max(-aa,-41.45);
	rl = 1.2*dig + 3.0;
	fnul = 10.0 + 6.0*(dig-3.0);
//C-----------------------------------------------------------------------------
//C     TEST FOR PROPER RANGE
//C-----------------------------------------------------------------------
	az = zabs(zr,zi);
	fn = fnu + (double)(n-1);
	aa = 0.5/tol;
	bb = (double)I1MACH[8]*0.5;
	aa = std::min(aa,bb);
	if(az>aa) goto II260;
	if(fn>aa) goto II260;
	aa = std::sqrt(aa);
	if(az>aa) *IERR = 3;
	if(fn>aa) *IERR = 3;
	znr = zr;
	zni = zi;
	csgnr = CONER;
	csgni = CONEI;
	if(zr>=0.0) goto II40;
	znr = -zr;
	zni = -zi;
//C-----------------------------------------------------------------------
//C     CALCULATE CSGN=EXP(FNU*PI*I) TO MINIMIZE LOSSES OF SIGNIFICANCE
//C     WHEN FNU IS LARGE
//C-----------------------------------------------------------------------
	inu = (int)fnu;
	arg = (fnu-(double)inu)*_PI_;
	if(zi<0.0) arg = -arg;
	csgnr = std::cos(arg);
	csgni = std::sin(arg);
	if((inu&1)==0) goto II40;
	csgnr = -csgnr;
	csgni = -csgni;
II40:
	zbinu(znr, zni, fnu, kode, n, CYR, CYI, NZ, rl, fnul, tol, elim, alim, debug);
	if(*NZ<0) goto II120;
	if(zr>=0.0) return;
//C-----------------------------------------------------------------------
//C     ANALYTIC CONTINUATION TO THE LEFT HALF PLANE
//C-----------------------------------------------------------------------
	nn = n - *NZ;
	if(nn==0) return;
	rtol = 1.0/tol;
	ascle = 1000.0*D1MACH[0]*rtol;
	for(i=1; i<=nn; i++) { //DO 50
//C       STR = CYR(I)*CSGNR - CYI(I)*CSGNI
//C       CYI(I) = CYR(I)*CSGNI + CYI(I)*CSGNR
//C       CYR(I) = STR
		aa = CYR[i-1];
		bb = CYI[i-1];
		atol = 1.0;
		if(std::max(std::abs(aa),std::abs(bb))>ascle) goto II55;
		aa = aa*rtol;
		bb = bb*rtol;
		atol = tol;
II55:
		str = aa*csgnr - bb*csgni;
		sti = aa*csgni + bb*csgnr;
		CYR[i-1] = str*atol;
		CYI[i-1] = sti*atol;
		csgnr = -csgnr;
		csgni = -csgni;
	} //CONTINUE 50
	return;
II120:
	if(*NZ==(-2)) goto II130;
	*NZ = 0;
	*IERR = 2;
	return;
II130:
	*NZ = 0;
	*IERR = 5;
	return;
II260:
	*NZ = 0;
	*IERR = 4;
	return;
}
//use: cacon, cbknu, cbunk, cuoik
void zbesk(double zr, double zi, double fnu, int kode, int n, double *CYR, double *CYI, int *NZ, int *IERR, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbesk\n");
	double aa, alim, aln, arg, az, bb, dig, elim, fn, fnul, rl, r1m5, tol, ufl;
	int    k, k1, k2, mr, nn, nuf, nw;

	*IERR = 0;
	*NZ = 0;
	if(zi==0.0 && zr==0.0) *IERR = 1;
	if(fnu<0.0) *IERR = 1;
	if(kode<1 || kode>2) *IERR = 1;
	if(n<1) *IERR = 1;
	if(*IERR!=0) return;
	nn = n;
//C-----------------------------------------------------------------------
//C     SET PARAMETERS RELATED TO MACHINE CONSTANTS.
//C     TOL IS THE APPROXIMATE UNIT ROUNDOFF LIMITED TO 1.0E-18.
//C     ELIM IS THE APPROXIMATE EXPONENTIAL OVER- AND UNDERFLOW LIMIT.
//C     EXP(-ELIM).LT.EXP(-ALIM)=EXP(-ELIM)/TOL    AND
//C     EXP(ELIM).GT.EXP(ALIM)=EXP(ELIM)*TOL       ARE INTERVALS NEAR
//C     UNDERFLOW AND OVERFLOW LIMITS WHERE SCALED ARITHMETIC IS DONE.
//C     RL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC EXPANSION FOR LARGE Z.
//C     DIG = NUMBER OF BASE 10 DIGITS IN TOL = 10**(-DIG).
//C     FNUL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC SERIES FOR LARGE FNU
//C-----------------------------------------------------------------------
	tol = std::max(D1MACH[3],1.0e-18);
	k1 = I1MACH[14];
	k2 = I1MACH[15];
	r1m5 = D1MACH[4];
	k = std::min(std::abs(k1),std::abs(k2));
	elim = LN10*((double)k*r1m5-3.0); //2.303*
	k1 = I1MACH[13] - 1;
	aa = r1m5*(double)k1;
	dig = std::min(aa,18.0);
	aa = aa*LN10; //*2.303
	alim = elim + std::max(-aa,-41.45);
	fnul = 10.0 + 6.0*(dig-3.0);
	rl = 1.2*dig + 3.0;
//C-----------------------------------------------------------------------------
//C     TEST FOR PROPER RANGE
//C-----------------------------------------------------------------------
	az = zabs(zr,zi);
	fn = fnu + (double)(nn-1);
	aa = 0.5/tol;
	bb = (double)I1MACH[8]*0.5;
	aa = std::min(aa,bb);
	if(az>aa) goto KK260;
	if(fn>aa) goto KK260;
	aa = std::sqrt(aa);
	if(az>aa) *IERR = 3;
	if(fn>aa) *IERR = 3;
//C-----------------------------------------------------------------------
//C     OVERFLOW TEST ON THE LAST MEMBER OF THE SEQUENCE
//C-----------------------------------------------------------------------
//C     UFL = DEXP(-ELIM)
	ufl = 1000.0*D1MACH[0];
	if(az<ufl) goto KK180;
	if(fnu>fnul) goto KK80;
	if(fn<=1.0) goto KK60;
	if(fn>2.0) goto KK50;
	if(az>tol) goto KK60;
	arg = 0.5*az;
	aln = -fn*std::log(arg);
	if(aln>elim) goto KK180;
	goto KK60;
KK50:
	zuoik(zr, zi, fnu, kode, 2, nn, CYR, CYI, &nuf, tol, elim, alim, debug);
	if(nuf<0) goto KK180;
	*NZ = *NZ + nuf;
	nn = nn - nuf;
//C-----------------------------------------------------------------------
//C     HERE NN=N OR NN=0 SINCE NUF=0,NN, OR -1 ON RETURN FROM CUOIK
//C     IF NUF=NN, THEN CY(I)=CZERO FOR ALL I
//C-----------------------------------------------------------------------
	if(nn==0) goto KK100;
KK60:
	if(zr<0.0) goto KK70;
//C-----------------------------------------------------------------------
//C     RIGHT HALF PLANE COMPUTATION, REAL(Z).GE.0.
//C-----------------------------------------------------------------------
	zbknu(zr, zi, fnu, kode, nn, CYR, CYI, &nw, tol, elim, alim, debug);
	if(nw<0) goto KK200;
	*NZ = nw;
	return;
//C-----------------------------------------------------------------------
//C     LEFT HALF PLANE COMPUTATION
//C     PI/2.LT.ARG(Z).LE.PI AND -PI.LT.ARG(Z).LT.-PI/2.
//C-----------------------------------------------------------------------
KK70:
	if(*NZ!=0) goto KK180;
	mr = 1;
	if(zi<0.0) mr = -1;
	zacon(zr, zi, fnu, kode, mr, nn, CYR, CYI, &nw, rl, fnul, tol, elim, alim, debug);
	if(nw<0) goto KK200;
	*NZ = nw;
	return;
//C-----------------------------------------------------------------------
//C     UNIFORM ASYMPTOTIC EXPANSIONS FOR FNU.GT.FNUL
//C-----------------------------------------------------------------------
KK80:
	mr = 0;
	if(zr>=0.0) goto KK90;
	mr = 1;
	if(zi<0.0) mr = -1;
KK90:
	zbunk(zr, zi, fnu, kode, mr, nn, CYR, CYI, &nw, tol, elim, alim, debug);
	if(nw<0) goto KK200;
	*NZ = *NZ + nw;
	return;
KK100:
	if(zr<0.0) goto KK180;
	return;
KK180:
	*NZ = 0;
	*IERR = 2;
	return;
KK200:
	if(nw==(-1)) goto KK180;
	*NZ = 0;
	*IERR = 5;
	return;
KK260:
	*NZ = 0;
	*IERR = 4;
	return;
}




//**************************************************
//**** Bessel J and Y                           ****
//**** Bessel function of the first/second kind ****
//**************************************************

//use: cbinu
void zbesj(double zr, double zi, double fnu, int kode, int n, double *CYR, double *CYI, int *NZ, int *IERR, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbesj\n");
	double aa, alim, arg, ascle, atol, az, bb, cii, csgni, csgnr, dig, elim, fn, fnul, rl, rtol, r1m5, \
	       sti, str, tol, zni, znr;
	int    i, inu, inuh, ir, k, k1, k2, nl;

	*IERR = 0;
	*NZ = 0;
	if(fnu<0.0) *IERR = 1;
	if(kode<1 || kode>2) *IERR = 1;
	if(n<1) *IERR = 1;
	if(*IERR!=0) return;
//C-----------------------------------------------------------------------
//C     SET PARAMETERS RELATED TO MACHINE CONSTANTS.
//C     TOL IS THE APPROXIMATE UNIT ROUNDOFF LIMITED TO 1.0E-18.
//C     ELIM IS THE APPROXIMATE EXPONENTIAL OVER- AND UNDERFLOW LIMIT.
//C     EXP(-ELIM).LT.EXP(-ALIM)=EXP(-ELIM)/TOL    AND
//C     EXP(ELIM).GT.EXP(ALIM)=EXP(ELIM)*TOL       ARE INTERVALS NEAR
//C     UNDERFLOW AND OVERFLOW LIMITS WHERE SCALED ARITHMETIC IS DONE.
//C     RL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC EXPANSION FOR LARGE Z.
//C     DIG = NUMBER OF BASE 10 DIGITS IN TOL = 10**(-DIG).
//C     FNUL IS THE LOWER BOUNDARY OF THE ASYMPTOTIC SERIES FOR LARGE FNU.
//C-----------------------------------------------------------------------
	tol = std::max(D1MACH[3],1.0e-18);
	k1 = I1MACH[14];
	k2 = I1MACH[15];
	r1m5 = D1MACH[4];
	k = std::min(std::abs(k1),std::abs(k2));
	elim = LN10*((double)k*r1m5-3.0); //2.303*
	k1 = I1MACH[13] - 1;
	aa = r1m5*(double)k1;
	dig = std::min(aa,18.0);
	aa = aa*LN10; //*2.303
	alim = elim + std::max(-aa,-41.45);
	rl = 1.2*dig + 3.0;
	fnul = 10.0 + 6.0*(dig-3.0);
//C-----------------------------------------------------------------------
//C     TEST FOR PROPER RANGE
//C-----------------------------------------------------------------------
	az = zabs(zr,zi);
	fn = fnu + (double)(n-1);
	aa = 0.5/tol;
	bb = (double)I1MACH[8]*0.5;
	aa = std::min(aa,bb);
	if(az>aa) goto JJ260;
	if(fn>aa) goto JJ260;
	aa = std::sqrt(aa);
	if(az>aa) *IERR = 3;
	if(fn>aa) *IERR = 3;
//C-----------------------------------------------------------------------
//C     CALCULATE CSGN=EXP(FNU*HPI*I) TO MINIMIZE LOSSES OF SIGNIFICANCE
//C     WHEN FNU IS LARGE
//C-----------------------------------------------------------------------
	cii = 1.0;
	inu = (int)fnu;
	inuh = inu/2;
	ir = inu - 2*inuh;
	arg = (fnu-(double)(inu-ir))*HPI;
	csgnr = std::cos(arg);
	csgni = std::sin(arg);
	if((inuh&1)==0) goto JJ40;
	csgnr = -csgnr;
	csgni = -csgni;
JJ40:
//C-----------------------------------------------------------------------
//C     ZN IS IN THE RIGHT HALF PLANE
//C-----------------------------------------------------------------------
	znr = zi;
	zni = -zr;
	if(zi>=0.0) goto JJ50;
	znr = -znr;
	zni = -zni;
	csgni = -csgni;
	cii = -cii;
JJ50:
	zbinu(znr, zni, fnu, kode, n, CYR, CYI, NZ, rl, fnul, tol, elim, alim, debug);
	if(*debug) PySys_WriteStdout("[DEBUG] ZBESJ: check res from ZBINU\n    NZ=%d  CYR=%16.8e CYI=%16.8e\n",\
	                             *NZ, CYR[0], CYI[0]);
	if(*NZ<0) goto JJ130;
	nl = n - *NZ;
	if(nl==0) return;
	rtol = 1.0/tol;
	ascle = 1000.0*D1MACH[0]*rtol;
	for(i=1; i<=nl; i++) { //DO 60
//C       STR = CYR(I)*CSGNR - CYI(I)*CSGNI
//C       CYI(I) = CYR(I)*CSGNI + CYI(I)*CSGNR
//C       CYR(I) = STR
		aa = CYR[i-1];
		bb = CYI[i-1];
		atol = 1.0;
		if(std::max(std::abs(aa),std::abs(bb))>ascle) goto JJ55;
		aa = aa*rtol;
		bb = bb*rtol;
		atol = tol;
JJ55:
		str = aa*csgnr - bb*csgni;
		sti = aa*csgni + bb*csgnr;
		CYR[i-1]= str*atol;
		CYI[i-1] = sti*atol;
		str = -csgni*cii;
		csgni = csgnr*cii;
		csgnr = str;
	} //CONTINUE 60
	return;
JJ130:
	if(*NZ==(-2)) goto JJ140;
	*NZ = 0;
	*IERR = 2;
	return;
JJ140:
	*NZ = 0;
	*IERR = 5;
	return;
JJ260:
	*NZ = 0;
	*IERR = 4;
	return;
}
//use: cbesh
void zbesy(double zr, double zi, double fnu, int kode, int n, double *CYR, double *CYI, int *NZ, double *CWORKR, double *CWORKI, int *IERR, int *debug) {
	if(*debug) PySys_WriteStdout("[DEBUG] called zbesy\n");
	double aa, ascle, atol, bb, c1i, c1r, c2i, c2r, elim, exi, exr, ey, hcii, rtol, r1m5, \
	       sti, str, tay, tol;
	int    i, k, k1, k2, nz1, nz2;

	*IERR = 0;
	*NZ = 0;
	if(zr==0.0 && zi==0.0) *IERR = 1;
	if(fnu<0.0) *IERR = 1;
	if(kode<1 || kode>2) *IERR = 1;
	if(n<1) *IERR = 1;
	if(*IERR!=0) return;
	hcii = 0.5;
	zbesh(zr, zi, fnu, kode, 1, n, CYR, CYI, &nz1, IERR, debug);
	if(*IERR!=0 && *IERR!=3) goto YY170;
	zbesh(zr, zi, fnu, kode, 2, n, CWORKR, CWORKI, &nz2, IERR, debug);
	if(*IERR!=0 && *IERR!=3) goto YY170;
	*NZ = std::min(nz1,nz2);
	if(kode==2) goto YY60;
	for(i=1; i<=n; i++) { //DO 50
		str = CWORKR[i-1] - CYR[i-1];
		sti = CWORKI[i-1] - CYI[i-1];
		CYR[i-1] = -sti*hcii;
		CYI[i-1] = str*hcii;
	} //CONTINUE 50
	return;
YY60:
	tol = std::max(D1MACH[3],1.0e-18);
	k1 = I1MACH[14];
	k2 = I1MACH[15];
	k = std::min(std::abs(k1),std::abs(k2));
	r1m5 = D1MACH[4];
//C-----------------------------------------------------------------------
//C     ELIM IS THE APPROXIMATE EXPONENTIAL UNDER- AND OVERFLOW LIMIT
//C-----------------------------------------------------------------------
	elim = LN10*((double)k*r1m5-3.0); //2.303*
	exr = std::cos(zr);
	exi = std::sin(zr);
	ey = 0.0;
	tay = std::abs(zi+zi);
	if(tay<elim) ey = std::exp(-tay);
	if(zi<0.0) goto YY90;
	c1r = exr*ey;
	c1i = exi*ey;
	c2r = exr;
	c2i = -exi;
YY70:
	*NZ = 0;
	rtol = 1.0/tol;
	ascle = 1000.0*D1MACH[0]*rtol;
	for(i=1; i<=n; i++) { //DO 80
//C       STR = C1R*CYR(I) - C1I*CYI(I)
//C       STI = C1R*CYI(I) + C1I*CYR(I)
//C       STR = -STR + C2R*CWRKR(I) - C2I*CWRKI(I)
//C       STI = -STI + C2R*CWRKI(I) + C2I*CWRKR(I)
//C       CYR(I) = -STI*HCII
//C       CYI(I) = STR*HCII
		aa = CWORKR[i-1];
		bb = CWORKI[i-1];
		atol = 1.0;
		if(std::max(std::abs(aa),std::abs(bb))>ascle) goto YY75;
		aa = aa*rtol;
		bb = bb*rtol;
		atol = tol;
YY75:
		str = (aa*c2r - bb*c2i)*atol;
		sti = (aa*c2i + bb*c2r)*atol;
		aa = CYR[i-1];
		bb = CYI[i-1];
		atol = 1.0;
		if(std::max(std::abs(aa),std::abs(bb))>ascle) goto YY85;
		aa = aa*rtol;
		bb = bb*rtol;
		atol = tol;
YY85:
		str = str - (aa*c1r - bb*c1i)*atol;
		sti = sti - (aa*c1i + bb*c1r)*atol;
		CYR[i-1] = -sti*hcii;
		CYI[i-1] =  str*hcii;
		if(str==0.0 && sti==0.0 && ey==0.0) *NZ = *NZ + 1;
	} //CONTINUE 80
	return;
YY90:
	c1r = exr;
	c1i = exi;
	c2r = exr*ey;
	c2i = -exi*ey;
	goto YY70;
YY170:
	*NZ = 0;
	return;
}




