from circuits import *
from zview import *
from properties import *

res1 = 100
cap1 = 1e-9
t1 = 1e-8
p1 = 0.5
t2 = 1e-6
p2 = 0.7

r = Resistor(res1)
c = Capacitor(cap1)
q = Q(t1, p1)
q2 = Q(t2, p2)
rc = r//c
rq = r//q
rc_df = rc.zdata_as_dataframe()
rq_df = rq.zdata_as_dataframe()
rc_rq = rc-rq
rc_rq_df = rc_rq.zdata_as_dataframe()
rc_rq_q = rc-rq-q2
rc_rq_q__df = rc_rq_q.zdata_as_dataframe()

rc_rq_q_alternative = (r//c)-(r//q)-q2
rc_rq_q_alternative__df = rc_rq_q_alternative.zdata_as_dataframe()

print(rc_rq_q_alternative__df)


""" r_0 = Resistor(100)
r_g = Resistor(1e8)
q_g = Q(2e-11,0.5)
r_par = Resistor(1e10)
q_par = Q(2e-10,1)
r_ser = Resistor(1e7)
q_ser = Q(2e-7,1)
q_ele = Q(2e-4,0.7)
r_ele = Resistor(1e13)
#rq_g = r_g//q_g
#rq_par = r_par//q_par
#rq_ser = r_ser//q_ser
#rq1 = rq_g//rq_par
#circuit = rq1-rq_ser
circuit = ((r_g//q_g)//(r_par//q_par))-(r_ser//q_ser)
freqs = [1,10,1e2,1e3,1e4,1e5,1e6]
circuit.zdata_to_zview(freqs, 'my_data.dat') """

#zviewcircuit = ZViewCircuit(r'd:\UFC\Dropbox\automaterials\QT.mdl')
#circuit = zviewcircuit.circuit
##circuit.zdata_to_csv()
#f = f_array(1e-3,1e6,20)
#dict_ = circuit.zdata_as_dict(f)
#print(dict_["f"], dict_["Z_re"], dict_["Z_im"])






