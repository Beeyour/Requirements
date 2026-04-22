from plantuml import PlantUML

def get_plantuml_svg(text):
    # إنشاء اتصال مع السيرفر الرسمي
    # ملاحظة: يمكنك تغيير الرابط لسيرفر محلي إذا كنت تستخدم Docker
    puml = PlantUML(url='https://www.plantuml.com/plantuml/svg/')
    
    # المكتبة تتكفل بالتشفير والضغط والـ Base64 المخصص
    try:
        svg_url = puml.get_url(text)
        return svg_url
    except Exception as e:
        return f"Error: {str(e)}"

# نص الـ Diagram الخاص بك
code = """@startuml
Alice -> Bob: Authentication Request
Bob -> Alice: Authentication Failure
group My own label [My own label 2]
    Alice -> Log : Log attack start
    loop 1000 times
        Alice -> Bob: DNS Attack
    end
    Alice -> Log : Log attack end
end
@enduml
"""

print(get_plantuml_svg(code))