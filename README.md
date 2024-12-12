Hier liegt der Code für die Webpage. Eine kruze Erklärung, falls weitere Fragen bestehen bitte per Mail oder LinkedIn melden.

Gehe auf Django/mypage

Erklärung der einzelnen Files:

- static/Images: Hier liegen die 960 Bilder die final in der Datenbank online gespeichert wurden

- db.sqlite3: Das ist die Datenbank selber, eine vorgefertigte SQLite Datenbank mit der dazugehörigen Logik

- manapge.py: Dies ist ein vorgefertigtes python Programm von Django. Das ist die grundlegende Django Funktionalität.
  Die ermöglicht Befehle mit denen sich der Server starten und beenden lässt, mit denen man Models updatet, und vieles mehr.

- mypage: Hier liegen verschiedenen Files die du zum Hosting benötigst und die settings.py file mit der man grundlegende Einstellungen einstellen kann.

-myapp: Hier liegen quasi alle Files um die Funktionalität der Webpage zu verändern. Hier musst du dran wenn du die Webpage anpassen willst.
Von daher klicke auf myapp um in die nächste Ebene zu gelangen.


Erklärung der einzelnen Files im Unterordner:

- _pychache_: Nicht wichtig für dich. Läuft im Hintergrund

- migrations: Nicht wichtig für dich. Wann immer man die Model Struktur anpasst muss man migraten mit der manage.py file.
  Alle migrations werden dann gespeichert, sodass man auf einen früheren Stand zurück gehen kann falls nötig. Die werden in diesem Ordner gespeichert.

- templates: Eine Webpage besteht aus mehreren Seiten, also z.B. der Home Seite, der "Kontakt Seite", der "Shopping Seite" etc.
  Jeder dieser Seiten braucht eine eigene HTML file. Das sind die Templates. Unsere Webpage hat insgesamt 11 verschiedene Templates:
  
	-home: Einstieg ins Experiment mit ein paar grundsätzlichen Erklärungen
	-user_data_input: Der erste Fragebogen vor dem Experiment
	-gallery_euclidian: Die Bilder für den formal space
	-gallery_social: Die Bilder für den social space
	-gallery_pheno: Die Bilder für den phenomenological space
	-gallery_intuitive: Die Bilder für den intuitive space
	-final_page: Der letzte Fragebogen nach dem Experiment
	-view_image: zur Vergrößerung eines einzelnen Bildes
	-add_image: Nur mit Adminrechten; ermöglicht neue Bilder in die Datenbank zu laden
	-add_completion_codes: Nur mit Adminrechten; ermöglicht neue CompletionCodes für MTurk in die Datenbank zu laden
	-update_Model_fields: Nur mit Adminrechten; ermöglicht per Excel file automatisiert die Werte der einzelnen Bilder anzupassen
Jede davon ist eine HTML file. HTML legt gewissermaßen die Optik in einer Art Baustein Logik fest. Falls du daran etwas verändern willst musst du den HTML Code
dementsprechend anpassen.

- _init_.py: Unwichtig für dich, läuft im Hintergrund

- models.py: Die Datenbanklogik der Webpage. Sehr wichtig! Das ist die Grundlage des gesamten Projektes. Es gibt verschiedene Models und jedes Model hat verschiedenen Attribute.
 Also z.B. das Model "Bild" mit den Attributen "filename", "image_data", "ai_answer", "correct_Answer" etc.
oder das Model "Visitor" mit den Attributen "session_id", "treatment_group", "gender", "age", etc.
Falls du also etwas an der grundlegenden Logik verändern willst, dann musst du diese File anpassen.

- admin.py: Jedes Django Project hat ein Admin Panel. Das ermöglicht dir intuitiv anzuschauen was auf der Webpage liegt, also welche Bilder, welche Visitors etc.
  Jedes Model das du auf dem Admin Panel sehen willst muss zuerst registriert werden. Das machst du in dieser File.
  Sobald es registriert ist siehst du das Model auf dem Admin Panel.
  Das Admin Panel erreicht man indem man den Link zur "home" Page mit einem /admin dahinter in den Browser eingibt.

-apps: Unwichtig für dich. Nur nötig falls man mehrere Apps auf einer Homepage laufen lassen will. Wir haben hier aber nur eine.

-forms: Habe ich nicht genutzt. Dies ermöglicht eine form, also z.B. den ersten Fragebogen einmal zu coden und anschließend an verschiedenen Stellen einzufügen. 
Nachdem ich ihn nur einmal gebraucht habe, habe ich ihn direkt im html template programmiert.

-test: Unwichtig. Nötig um Test durchzuführen

-urls: Hier legst du deine URL Struktur fest. Der Hauptlink zur Homepage wird später beim hosten festgelegt und steht noch nicht fest. 
Alle "Unterlinks" legst du allerdings hier fest. Also z.B. www.hauptlink/gallery_social.com führt zum Template "gallery_social". 
Für jede der 11 Templates muss ein url link definiert werden.

-views: Hier wirst du am meisten dran arbeiten müssen. Das ist die Logik der gesamten Webpage. 
Was passiert wenn man auf einen Button drückt. Welche Bilder werden auf welches Template geladen. 
Welche Messages erhalten user in welchen Fällen. Was wird abgespeichert, was wird geladen, welche Berechnungen werden durchgeführt.
Hier kann ich also z.B. den Wert eines Attributes eines Models aus der Datenbank laden und damit irgendwas machen.
All das wird für jedes Template hier festgelegt. Neben den 11 Templates liegen hier zudem einen Vielzahl von Funktionen die für verschiedene Aufgaben und Berechnungen genutzt werden.
Diese File ist ziemlich lang und hat 1818 Zeilen. Falls du hier Hilfe brauchst schreib mir.
