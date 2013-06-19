MACHINE           Locks
/* This B Machine is taken from the book: The B-Method: An Introduction
   (Editor Palgrave, ISBN 0-33-79284-X, Year 2002) by Steve Schneider.
   This machine is distributed with kind permission by Steve Schneider.
*/
INCLUDES          Doors

PROMOTES          closedoor

SETS              STATUS = {locked, unlocked}

VARIABLES         status

INVARIANT         status : DOOR --> STATUS & position~[{open}] <: status~[{unlocked}]

INITIALISATION    status := DOOR * {locked}

OPERATIONS

  opendoor(dd) =
  PRE dd : DOOR & status(dd) = unlocked
  THEN opening(dd)
  END;

unlockdoor(dd) =
  PRE dd : DOOR
  THEN status(dd) := unlocked
  END;

lockdoor(dd) =
  PRE dd : DOOR & position(dd) = closed
  THEN status(dd) := locked
  END

END
