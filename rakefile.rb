PYTHON_SETUP_FILE = File.join(__dir__, "setup.py")
PYTHON_REQUIREMENTS_FILE = File.join(__dir__, "requirements.txt")
DIST_DIRECTORY = File.join(__dir__, "dist")
VERSION_FILE_ARTIFACT = File.join(DIST_DIRECTORY, ".version")

desc "Install the requirements from the requirements file.  Uses 'pip' with the '--user' flag"
task :python_requirements do
  sh "python3 -m pip install -r #{PYTHON_REQUIREMENTS_FILE} --user"
end

desc "Install the Python library from source.  Uses 'pip' with the '--user' flag."
task :python_install do
  sh "python3 -m pip install ."
end

desc "Build a python release package"
task :python_release do
  # Build a release wheel for the Python package
  sh "python3 setup.py bdist_wheel"
end

task :requirements => :python_requirements do
end

task :install => :python_install do
end

task :test => :python_test do
end

task :release => :python_release do
end