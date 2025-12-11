# INSTRUCTIONS FOR "cengage/answer_highlighter.py"

Load the Extension in Burp:

- Open Burp Suite.
- Go to the Extensions tab.
- In the Extensions sub-tab "Installed", click Add on the left side.
- In the popup:
  - Extension type: Select "Python".
  - Extension file: Browse to your answer_highlighter.py file (for example: extensions/answer_highlighter.py).
- Click Next. Burp will load the extension.
- Check the Output or Errors tab in Extender for any issues. You should see a message like:
  - "Answer Highlighter extension loaded..." in the output when it loads successfully.

Troubleshooting / notes:

- If the "Python" option is not available, configure a Python runtime for Burp (typically by pointing Burp to a Jython standalone JAR in Extender → Options → Python environment).
- Check the Output/Errors tab for import errors or stack traces — missing dependencies and incompatible Python/Jython versions are common causes.
- Make sure the .py file is readable by Burp and that you selected the correct file path.
- If you modify the extension after loading, right click the loaded extension and press "reload" in the context menu.
