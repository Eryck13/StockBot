import plotly.express as px
import pandas as pd

# Create a dataframe with the x and y data
df = pd.DataFrame({'x': [1653399000, 1653485400, 1653571800, 1653658200, 1653917400, 1654003800, 1654090200, 1654176600, 1654263000, 1654522200, 1654608600],
                   'y': [20286.19921875, 20383.80078125, 20532.19921875, 20748.599609375, 20919.400390625, 20729.30078125, 20713.69921875, 21031.80078125, 20790.69921875, 20819.099609375, 20928.19921875]})

# Plot the data using Plotly express
fig = px.line(df, x='x', y='y')
fig.show()