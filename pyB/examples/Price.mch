MACHINE           Price

SEES              Goods

VARIABLES         price

INVARIANT         price : GOODS --> NAT1

INITIALISATION    price :: GOODS --> NAT1

OPERATIONS

  setprice(gg,pp) =
  PRE gg : GOODS & pp : NAT1
  THEN price(gg) := pp
  END;

pp2 <-- pricequery(gg2) =
  PRE gg2 : GOODS THEN pp2 := price(gg2) END

END
