MACHINE KnightsKnaves
/* Puzzle from Smullyan:
 Knights: always tell the truth
 Knaves: always lie

 1: A says: “B is a knave or C is a knave”
 2: B says “A is a knight”

 What are A & B & C?
*/
CONSTANTS A,B,C
PROPERTIES
 A:BOOL & B:BOOL & C:BOOL /* TRUE if they are a Knight */
 &
 (A=TRUE <=> (B=FALSE or C=FALSE)) &
 (B=TRUE <=> A=TRUE)
END

