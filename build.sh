git clone https://github.com/bendisposto/probparsers.git
cd probparsers/
./gradlew jar
svn co https://cobra.cs.uni-duesseldorf.de/prob/branches/witulski/jars/
svn co https://cobra.cs.uni-duesseldorf.de/prob/branches/witulski/pyB/
cp jars/parserbase-2.0.67.jar  parserbase/build/libs/
cp jars/prologlib-2.0.67.jar  prologlib/build/libs/
cp jars/cliparser-2.0.67.jar cliparser/build/libs/
cp jars/bparser-2.0.67.jar bparser/build/libs/
cd pyB/
py.test

