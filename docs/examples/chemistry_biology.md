# Chemistry and Biology

Example script showing how to use the [ChemistryBiology][msl.kcdb.chemistry_biology.ChemistryBiology] class to extract information from the KCDB.

## Script

<!-- fmt: off -->
```python
--8<-- "examples/chemistry_biology.py"
```
<!-- fmt: on -->

## Output

Running this script outputs the following, although, some values may change from what you observe when you run this script since information in the KCDB is continually changing.

```
Getting all reference data for Chemistry and Biology...
  There are 105 countries
  There are 1754 analytes
  There are 15 categories
All analytes related to 'boron'...
  Analyte(id=2, label='boron', value='boron')
All NMIs that have capabilities with 'boron' analytes...
  NIST (Advanced materials): 8395201
  NIST (Advanced materials): 8395202
  NIST (Advanced materials): 8395206
  NIST (Inorganic solutions): 8391106
  KRISS (Inorganic solutions): 105-02-BX2
  BAM (Inorganic solutions): InorgSol-7
  BAM (Inorganic solutions): InorgSol-15
  BAM (Inorganic solutions): InorgSol-16
  SMU (Inorganic solutions): I-10-20
  UME (Water): G3IK-3110
  NIM (Water): Water-2
  VNIIM (Water): 5.1-06
  NMIJ AIST (Water): 5-01-05
  NMIJ AIST (Food): 7505-02
  NRC (Food): MEF-37
  NRC (Water): TEW42
  NMIJ AIST (Inorganic solutions): NMIJ CRM 3627
```