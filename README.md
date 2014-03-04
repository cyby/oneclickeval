OneClickEval
============

Options:
  -h, --help            show this help message and exit
  --iunit=IUNIT_FILENAME
                        iUnit filename
  --mat=MATCH_FILENAME  Match filename
  --maxlen=MAXLEN       maximum length of X-string
  -l L                  parameter of S-measure
  --beta=BETA           parameter of S#-measure


Evaluation tool for 1CLICK task

A ".iunits" file is of the following format:
% cat 1C2-J.iunits
1C2-J-0001 I001 3 10
1C2-J-0001 I002 1 5 I001
1C2-J-0001 I003 3 5 I002
1C2-J-0002 I001 2 2
1C2-J-0002 I002 6 5
1C2-J-0002 I003 2 3 I001,I002

where
Field 1: question ID;
Field 2: iUnit ID;
Field 3: iUnit weight (i.e. importance);
Field 4: vital string length. A vital string is a short text string
         that is probably necessary to be included in the 1CLICK system output
	     in order to cover the meaning of the iUnit in the system output;
Field 5: entailed iUnit ID(s). iUnit x is entailed by iUnit y if y includes x.
         For example, an iUnit 'got PhD in 2010' entails another 'got PhD'.
         Please list iUnit IDs that are entailed by the iUnit 
         separating them with ','.


A batch match file looks like this:
% cat 1CLICKRUN-D-1
1C2-J-0001 syslen= 500
1C2-J-0001 I001 100
1C2-J-0001 I002 50
1C2-J-0002 syslen= 10
1C2-J-0002 I002 400

where (except for the 1st line that shows the
actual size of the X-string)
Field 1: question ID;
Field 2: iUnit ID of the iUnit identified by the assessor in the output;
Field 3: iUnit offset (position) as identified by the assessor.
