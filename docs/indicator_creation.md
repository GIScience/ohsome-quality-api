## Indicator Creation Guide

To make contribution to the OQT easier we have compiled this guide which explains the parts that are needed to built an indicator.<br>
If you want to create an indicator you need to create **two** files in a folder named after your indicator which is placed in **ohsome_quality_tool/indicators** e.g. ohsome_quality_tool/indicators/your_indicator_name.<br>
The two files are named:

1. **metadata.yaml**
2. **indicator.py**

### metadata.yaml

The metadata.yaml holds basic information about your indicator e.g. the indicator name, a quick description on what it does and how it works and a standartized interpretation of it's possible results.<br>
The easiest way to setup the metadata.yaml the right way would be to copy it from another indicator and to replace the texts with your own. Just don't replace or change the category names.

### indicator.py

To illustrate the structure of an indicator we created a Class Diagram showing it's most important components. 
<div align="center">
  <img src="./UML-Class-Diagram.png">
</div>

As you can see the indicator you are trying to create should inherit from BaseIndicator. This class takes care of most of the needed functionality. The BaseIndicator is built from three elements: Result, Metadata and Layer, and some utility functions. The Metadata is automatically loaded from it's corresponding metadata.yaml, the layer can be set during object creation and the result saves the result of a Indicator instance. if you do not need a very specific custom layer you can ignore this component.

In your own indicator.py you only need to implement the three functions "preprocess", "calculate" and "create_figure" as well as an __init__ function which is called to create an instance of your indicator. The rest is working through inherited functionalities.

#### init
Your init should look like this:
```python
def __init__(
      self,
      dynamic: bool,
      layer_name: str,
      dataset: str = None,
      feature_id: int = None,
      bpolys: FeatureCollection = None,
  ) -> None:
      super().__init__(
          dataset=dataset,
          feature_id=feature_id,
          dynamic=dynamic,
          layer_name=layer_name,
          bpolys=bpolys,
      )
```

Additionally you can define variable placeholders for important values and preliminary results here.

#### preprocess

This function should be used to gather and preprocess the needed data for your indicator. Usually you will need to get the features specified in your layer through the **query** helper function which is can be imported from **ohsome_quality_tool/ohsome/client**. This function can be called with a layer and a Bounding-Multipolygon and returns the the resulting objects by calling the ohsomeAPI. If you need additional data, e.g. the population in an area, you should prepare it here too.

#### calculate

Here you should execute all needed calculations and save the results in your result object (**self.result.label, self.result.value and self.result.description**). 

#### create_figure

Finally you need to create a svg figure (e.g. with matplotlib) and save it to **self.result.svg** (e.g. plt.savefig(self.result.svg, format="svg")). This class attribute is created on initialization in the BaseIndicator class and holds a unique path.
