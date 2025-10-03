# ImposiPDF

ImposiPDF est un outil Python pour imposer les pages d’un PDF en format cahier avec traits de coupe.  
Il permet de transformer un PDF standard en un PDF prêt à être imprimé en livret.

---

## Contenu du dossier

Le dossier `ImposiPDF` contient :  
- `ImposiPDF.py` → le script principal  
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
2. **Ouvrir le [terminal](https://codeur-pro.fr/invite-de-commande-et-terminal/)** (ou PowerShell sur Windows) dans le dossier `ImposiPDF`.
3. **Se rendre dans le dossier qui contient requirements.txt** avec la commande
```bash
cd /Users/[chemin vers le dossier correspondant]/ImposiPDF
```

4. **Installer les modules nécessaires** avec la commande suivante :

```bash
pip install -r requirements.txt
```

## Transformer le script en exécutable (application)
### Sur Windows

1. Double-cliquer sur l'application `ImposiPDF.bat`.
2. Suivre les instructions à l’écran :
- Indiquer le chemin du fichier PDF à imposer.
- Entrer le nom du fichier PDF de sortie (sans extension).
3. Le PDF imposé sera généré dans le même dossier.

### Sur macOS / Linux

1. Ouvrir un terminal dans le dossier `ImposiPDF`.
2. Créer une application à partir du script :
``` bash
chmod +x ImposiPDF.py
```

3. Ouvrir `ImposiPDF.app`
4. Suivre les instructions à l’écran.
