import pyqdpx
qdpx = pyqdpx.QDPX("oltas_teszt.qdpx")
project = qdpx.get_project()
videos_selection = project.sources['68bbdc14-c361-4432-b4dd-ae1dbfc12890']

new_user = pyqdpx.User(name="test_user", id="test")
project.add_user(new_user)

videos_selection.add_selection(start=291455, end=292267, user=new_user, code=project.find_code("Epistemic superiority"))
videos_selection.add_selection(start=291455, end=292267, user=new_user, code=project.find_code("Anecdotal evidence"))
videos_selection.add_selection(start=291455, end=292267, user=new_user, code=project.find_code("Toxicity hazard"))

videos_selection.add_selection(start=292432, end=293248, user=new_user, code=project.find_code("Made-up threat"))
videos_selection.add_selection(start=292432, end=293248, user=new_user, code=project.find_code("+Media"))
videos_selection.add_selection(start=292432, end=293248, user=new_user, code=project.find_code("Financial interests"))
videos_selection.add_selection(start=292432, end=293248, user=new_user, code=project.find_code("+Lethal consequences of vaccination"))
videos_selection.add_selection(start=292432, end=293248, user=new_user, code=project.find_code("Epistemic superiority"))

videos_selection.add_selection(start=293413, end=294277, user=new_user, code=project.find_code("Made-up threat"))
videos_selection.add_selection(start=293413, end=294277, user=new_user, code=project.find_code("+Media"))
videos_selection.add_selection(start=293413, end=294277, user=new_user, code=project.find_code("Financial interests"))
videos_selection.add_selection(start=293413, end=294277, user=new_user, code=project.find_code("+Lethal consequences of vaccination"))
videos_selection.add_selection(start=293413, end=294277, user=new_user, code=project.find_code("Epistemic superiority"))

videos_selection.add_selection(start=294437, end=294657, user=new_user, code=project.find_code("Side effects"))
videos_selection.add_selection(start=294437, end=294657, user=new_user, code=project.find_code("Anecdotal evidence"))

videos_selection.add_selection(start=294822, end=295032, user=new_user, code=project.find_code("1. Conspiracist ideation"))
videos_selection.add_selection(start=294822, end=295032, user=new_user, code=project.find_code("Do your own research"))

videos_selection.add_selection(start=295190, end=295440, user=new_user, code=project.find_code("1. Conspiracist ideation"))
videos_selection.add_selection(start=295190, end=295440, user=new_user, code=project.find_code("3. Unwarranted beliefs"))

videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("Targeting the disadvantaged"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("+Government"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("Systemic corruption"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("Disease disappears by itself"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("Politicization of vaccines"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("Disease is not serious"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("Resisting coercion"))
videos_selection.add_selection(start=295605, end=297186, user=new_user, code=project.find_code("+Belief in artificial origin of the virus"))

videos_selection.coded_selections['3c23e29e-8f82-4fae-88dd-ae1f25876826'].end = 50700
videos_selection.coded_selections['e3a6e477-2b94-48fd-a9dd-ae1f25874146'].end = 50700
videos_selection.coded_selections['acf60ed5-af6d-4dc6-86dd-ae1f2587417d'].end = 50700
videos_selection.coded_selections['c64be640-519e-409f-a6dd-ae1f258741b3'].end = 50700

project.save()