MACHINE Laundry_Controlsystem_n_machines

SETS
   door_positions = {opened, closed};
   switch_mode = {on, off}

CONSTANTS
   total, /* represents the number of washing machines in the self-service laundry */
   max_weight /* maximum weight of laundry per washing machine */

VARIABLES 
   door, switcher, water_in_machine, paid, busy ,laundry_weight

PROPERTIES
     total : NATURAL & total = 5
   & max_weight : NATURAL & max_weight = 2

INVARIANT
   /* basic requirements */
   paid: 1..total --> BOOL & 
   door: 1..total --> door_positions & 
   switcher: 1..total --> switch_mode &
   water_in_machine: 1..total --> BOOL &
   busy : (1..total --> BOOL) &
   laundry_weight: 1..total --> 0..max_weight &

   /* safety requirements */
   !(i).(paid(i) = FALSE => switcher(i) = off) &
   !(i).(switcher(i) = on => door(i) = closed) &
   !(i).(water_in_machine(i) = TRUE => switcher(i) = on) &
   !(i).(laundry_weight(i) >1 => switcher(i) = off)
   
INITIALISATION 
    busy := (1..total)*{FALSE} || paid := (1..total)*{FALSE} ||
    switcher := (1..total)*{off} || door := (1..total)*{closed} ||
    water_in_machine := (1..total)*{FALSE} || laundry_weight := (1..total)*{0}

OPERATIONS
  Open_Door(n) = 
     PRE
          n : 1..total &
          switcher(n)=off & 
          door(n)=closed 
     THEN 
          door(n):=opened
     END;

  Put_In_Laundry(n) = 
     PRE 
          n : 1..total &
          door(n)=opened & 
          laundry_weight(n)<max_weight
     THEN 
          laundry_weight(n):= laundry_weight(n)+1
     END;

  Close_Door(n) = 
     PRE 
          n : 1..total &
          door(n)=opened 
     THEN 
          door(n):=closed 
     END;


  Pay(n) = 
     PRE 
          n:1..total & 
          paid(n)=FALSE & 
          switcher(n)=off
     THEN 
	paid(n):=TRUE
     END;

  Put_On(n) = 
     PRE 
        n:1..total & 
        paid(n)=TRUE & 
        door(n)=closed & 
        laundry_weight(n)<max_weight & 
        switcher(n)=off
     THEN 
		switcher(n):=on || water_in_machine(n):=TRUE
     END;

  Finished(n) = 
     PRE 
        n : 1..total & 
        switcher(n)=on
     THEN 
        switcher(n):=off || water_in_machine(n):=FALSE || paid(n):=FALSE
     END;



  Put_Out_Laundry(n) = 
     PRE 
        n : 1..total & 
        door(n)=opened & 
        laundry_weight(n)>0
     THEN 
        laundry_weight(n):= laundry_weight(n)-1
     END

END


