import folium

from branca.element import Template, MacroElement
import webbrowser

lat = 44.372387781
long = 3.806467262

map1 = folium.Map(location=(lat - 0.00150, long), width=1800, height=1400, zoom_start=18, control_scale=True)
folium.Marker((lat, long),popup="Station").add_to(map1)

#dark_basemap = folium.TileLayer("cartodbdark_matter", name="Dark Theme Basemap").add_to(map1)

textbox_css = f"""
{{% macro html(this, kwargs) %}}
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Prévision débit cours d'eau</title>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" integrity="sha512-MV7K8+y+gLIBoVD59lQIYicR65iaqukzvf/nwasF0nqhPay5w/9lJmVM2hMDcnK1OnMGCdVK+iQrJ7lzPJQd1w==" crossorigin="anonymous" referrerpolicy="no-referrer"/>
    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

    <script>
      $( function() {{
        $( "#textbox" ).draggable({{
          start: function (event, ui) {{
            $(this).css({{
              right: "auto",
              top: "auto",
              bottom: "auto"
            }});
          }}
        }});
      }});
    </script>
  </head>

  <body>
    <div id="textbox" class="textbox">
      <div class="textbox-title">Données sur le cours d'eau</div>
      <div class="textbox-content">
        <p>Ville : Saint-Maurice-de-Ventalon</p>
        <p>Cours d'eau : Le Tarn</p>
        <p>Latitude de la station {lat}</p>
        <p>Longitude de la station {long}</p>
        <p>Prévision a J+1 : R2 : 0.94</p>
        <p>Prévision a J+2 : R2 : 0.91</p>
        <p>Prévision a J+3 : R2 : 0.80</p>
        <p>Prévision a J+4 : R2 : 0.67</p>
      </div>
    </div>
 
</body>
</html>

<style type='text/css'>
  .textbox {{
    position: absolute;
    z-index:9999;
    border-radius:4px;
    background: white;
    box-shadow: 0 8px 32px 0 rgba( 31, 38, 135, 0.37 );
    border: 4px solid rgba( 215, 164, 93, 0.2 );
    padding: 10px;
    font-size:14px;
    right: 20px;
    bottom: 20px;
    color: black;
  }}
  .textbox .textbox-title {{
    color: black;
    text-align: center;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 22px;
    }}
</style>
{{% endmacro %}}
"""

my_custom_style = MacroElement()
my_custom_style._template = Template(textbox_css)

map1.get_root().add_child(my_custom_style)

folium.LayerControl(collapsed=False).add_to(map1)

map1.save(r"\map.html")

webbrowser.open(r"\map.html")