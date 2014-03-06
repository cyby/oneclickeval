OneClickEval
============

OneClickEval is an evaluation tool for 1CLICK-2@NTCIR-10.

Usage
------------
```
Usage: eval_oneclick [options]

Options:
  -h, --help            	show this help message and exit
  --iunit=IUNIT_FILENAME	iUnit filename
  --mat=MATCH_FILENAME  	Match filename
  --maxlen=MAXLEN       	maximum length of X-string
  --l=L						parameter of S-measure
  --beta=BETA           	parameter of S#-measure
```

e.g.
```
eval_oneclick --iunit=1C2-J.iunits.tsv --mat=KUIDL-J-D-MAND-1.tsv --maxlen=500 --l=1000 --beta=10
```


iUnits File
------------
An iUnit file is of the following format:

```
% cat 1C2-J.iunits
1C2-J-0001 I001 3 10
1C2-J-0001 I002 1 5 I001
1C2-J-0001 I003 3 5 I002
1C2-J-0002 I001 2 2
1C2-J-0002 I002 6 5
1C2-J-0002 I003 2 3 I001,I002
````

where
- Field 1: query ID;
- Field 2: iUnit ID;
- Field 3: iUnit weight (i.e. importance);
- Field 4: vital string length;
- Field 5: entailed iUnit ID(s). A list of iUnit IDs that are entailed by the iUnit 
           separating them with ','.


Match File
------------
A match file is of the following format:
```
% cat 1CLICKRUN-D-1
1C2-J-0001 syslen= 500
1C2-J-0001 I001 100
1C2-J-0001 I002 50
1C2-J-0002 syslen= 10
1C2-J-0002 I002 400
```

More precisely,
```
<queryID1>[TAB]syslen=[TAB]<syslen1>
<queryID1>[TAB]<iUnitID1>[TAB]<offset1>
<queryID1>[TAB]<iUnitID2>[TAB]<offset2>
...
<queryID2>[TAB]syslen=[TAB]<syslen2>
...
```

where
- &lt;syslen>: the length of the X-string;
- &lt;offset>: the offset of an iUnit identified by assessors.
