from plantuml import PlantUML

def get_plantuml_svg(text):

    puml = PlantUML(url='https://www.plantuml.com/plantuml/svg/')
    try:
        svg_url = puml.get_url(text)
        return svg_url
    except Exception as e:
        return f"Error: {str(e)}"
