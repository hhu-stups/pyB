MCH = Lift2.mch         # Table 6.1
MCH = SetUnion.mch      # Table 6.2
MCH = WhileLoop.mch     # Table 6.3
MCH = WhileLoop2.mch    # Table 6.4
MCH = SigmaLoop.mch     # Table 6.5
MCH = SigmaLoop2.mch     # Table 6.5
echo "+++++++"
echo $MCH
echo "+++++++"
time ./pyB_RPython-c -mc examples/rpython_performance/Lift2.mch 
time PYTHONPATH=.:../pypy python pyB_RPython.py -mc examples/rpython_performance/Lift2.mch
time python pyB.py -mc examples/rpython_performance/Lift2.mch
time ../ProB/probcli -mc 2147483648 -p MAXINT 2147483648 -p MININT -2147483648 -p TIME_OUT 2147483648 examples/rpython_performance/Lift2.mch