# ImposiPDF

ImposiPDF est un outil Python pour imposer les pages d’un PDF en format cahier avec traits de coupe.  
Il permet de transformer un PDF standard en un PDF prêt à être imprimé en livret.

---

## Contenu du dossier

Le dossier `ImposiPDF` contient :
- `ImposiPDF.bat` → fichier éxecutable Windows
- `ImposiPDF.py` → le script principal
- `logo-imposition.ico` → logo de l'outil
- `requirements.txt` → liste des modules Python nécessaires
---

## Prérequis

- **Dernière version de Python** : [Télécharger Python](https://www.python.org/downloads/)  
- **Pip** (installé automatiquement avec Python)

Si python est déjà installé sur votre ordinateur, vérifiez les versions de python et pip.

Si vous rencontrez un problème sous Windows lors des étapes suivantes : 
1. Désinstallez Python
2. Réinstallez le manuellement en personnalisant l'installation : assurez-vous ainsi que sont activés :
- "pip"
- "Add python to environnemental variables"
3. Finaliser l'installation.

---

## Étapes d’installation

1. **Télécharger le dossier `ImposiPDF`** sur votre ordinateur.

### **Sur Windows**

1. Double-cliquer sur l'application `ImposiPDF.bat`.
2. Suivre les instructions à l’écran :
- Indiquer le chemin du fichier PDF à imposer.
- Entrer le nom du fichier PDF de sortie (sans extension).
3. Le PDF imposé sera généré dans le même dossier.

### **Sur MacOS**

Si vous voulez utiliser **ImposiPDF** sans ouvrir le Terminal, vous pouvez créer une **application Automator** qui lance le script en un clic.

1. **Ouvrir Automator**  
   - Ouvrez Spotlight (`Cmd + Espace`)  
   - Tapez `Automator` et ouvrez le logiciel  
   - Une fois le logiciel lancé, créer un **Nouveau Document**, choisissez le type **Application**, puis cliquez sur **Choisir**

2. **Ajouter un script**  
   - Dans la colonne de gauche : **Bibliothèque → Utilitaires → Exécuter un script AppleScript**  
   - Faites glisser cette action dans la zone principale

3. **Coller le code suivant dans l'espace éditable**  
   Remplacez le chemin par le chemin exact de votre fichier `ImposiPDF.py` :

   ```applescript
   on run {input, parameters}
       tell application "Terminal"
           activate
           do script "python3 '/Chemin/vers/ImposiPDF.py'"
       end tell
       return input
   end run
   ```

4. **Enregistrer l’application**
   - Menu `Fichier` → Enregistrer
   - Nom : `ImposiPDF.app`
   - Emplacement : `Bureau` ou dossier `Applications`

   - Pour ajouter une icône, suivre les instructions suivantes :

<img src="readme-instructions_ouvrir-les-informations.png" alt="Ouvrir les informations" height="300px" />
<video controls height="300px"><source src="readme-instructions_ajout-icone.mp4" type="video/mp4" />Votre navigateur ne supporte pas la vidéo.</video>

5. **Tester**
   - Double-cliquez sur l’icône ImposiPDF.app
   - Le Terminal s’ouvre et le script démarre automatiquement

### **Sur Linux**

1. **Ouvrir le terminal**
2. **Se rendre dans le dossier `ImposiPDF`** avec la commande (le dossier dans lequel se trouve le fichier `requirements.txt`)

```bash
cd /Users/[chemin vers le dossier correspondant]/ImposiPDF
```
3. **Installer les modules nécessaires** avec la commande suivante :

```bash
pip install -r requirements.txt
```

4. **Éxécuter le script :**

``` bash
chmod +x ImposiPDF.py
```
3. Lancer le programme :
``` bash
./ImposiPDF.py
```

4. Suivre les instructions à l’écran.

5. Vous pouvez maintenant déplacer le dossier `ImposiPDF` (pas `ImposiPDF-main`) à l'endroit qui vous arrange.

#### Maintenant que vous avez installé le programme, vous n'aurez plus qu'à écrire cette ligne pour l'utiliser n'importe quand :
``` bash
./[chemin vers le dossier correspondant]/ImposiPDF.py
```
Conseil : réécrivez la ligne avec le bon chemin et notez la pour vous faire gagner du temps. par exemple :
``` bash
./Users/Desktop/ImposiPDF/ImposiPDF.py
```
