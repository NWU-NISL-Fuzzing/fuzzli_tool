var NISLFuzzingFunc = 
function(a, b) {
    return JSON.stringify(a[0]).localeCompare(JSON.stringify(b[0]));
}
;
var NISLParameter0 = [false, true, true, true];
var NISLParameter1 = ["RcB;PBz\"Mw\",qTy~fb+QCpn\"qX?5!I0&|,U#!+?E~&988ae_r(gm^T Kx5X:5_(l|oRKexA5])?-D8l[2/Bx}1Sk:vJ145\\+*Z]-5HS@ lV:UYVgD[Qb[9S6W #j--V5", "Wi\"DPbU?6z~!J\\F\"#bXOCAi@op<\\XA(zl89KNw'i$n8UScffkfT|dzjSo:c( oVivRd]$8L^?xp", "Y0JUc=D6#|l!Ol8L]<klo:wT4unABQ1`3.jy{q ,u4 ;vIQaY\"wbL# s{s5=KFsV@EF_+)oB?EVefrJwM~Hx3)|n3m7Zz", "zdYQ\\(WF1IW?D1E&a\\@Z2&P=Prm ]Ly<a4 eFZv9ywjgNS4nN~NKVx_/7`8?~ovk>rh'AY=<9y\\Xj0WfWE$;fR.\"<-f+vj", "7.3tzRxS!LXlb!!l; iw:B:nVS)w(6_<>&1=hG4PdE|JL+$>L|%RUP#MNR5l ~hlQOJGxk\\pQ+UuY@-bQR$", "z|1W+bebp2o*M2H6WFVEdG{C${*mmLaUqXb\":t5pmE8|zV;#8", "d4-=\"c+oOcAZ]{7]T5C3/s", "U-Oyq&~<'`1S8{4mc@yQu3f4Vh!`Jw|[pR+C&%81Qh&K&6aADWa5ZRPi,oGxdx4sZ7 t8A", "v}DYUszQj<^_JYD", "m&9ZJm0W-p[XX5.-/DR|{J/wUV`j>'o%~`]EISUX<QY;3uW", "?`ks6T:]$&n:#]DMrp*;pkqq}y[Vp!zaA0;P3[Mom/R:Nkslx9RV?:gvO{]KI|", "2Tx~3{L~]LJB@uEW{~49f2qbN2tqzR", "T&?D}i}^-,p&pT6PBx8$N]a 7%w3D$QeKQlRih+mXbgA@p|8QPZI6|*yrpu*59GqCox>KzNFpOb w<MRuTVH", "Ab9sIzsB&6^h]_\":#i$1wfcE*swA|+tf%sBVi-", "*6&0 -0K|V0Cbv}yQwi<K1[5G0?//\\.[\"tw57n\"Sqp'_sU-Eq7mVoDWKhfO}YA[;_9<5/fpO", "3U`P_v2'+pc0`"];
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0, NISLParameter1);
print(NISLCallingResult);