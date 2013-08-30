from django.conf import settings
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django import forms
from pleiades import pleiades_settings

JAR_CHOICES = (('Custom','Custom Jar File'),
               ('Master', 'Current Master Branch (' + pleiades_settings.cilib_snapshot_version + ')')
              )

class UploadForm(forms.Form):
    job_name = forms.CharField(max_length=100, required=True)
    algorithm_input_file = forms.FileField(required=True)
    problems_input_file = forms.FileField(required=True)
    jar_options = forms.ChoiceField(widget=forms.RadioSelect(attrs={'onclick':'if (this.value != "Custom"){document.getElementById("id_custom_jar_file").disabled=1} else {document.getElementById("id_custom_jar_file").disabled=0}'}),
                                    choices=JAR_CHOICES, required=True, initial='Master')
    custom_jar_file = forms.FileField(required=False)
    custom_jar_file.widget.attrs['disabled'] = True
    min_solutions = forms.ChoiceField(label='Minimum solutions',
    	choices=[(5, 5), (10, 10), (15, 15)]
    )
    min_problems = forms.ChoiceField(label='Minimum problems',
    	choices=[(5, 5), (10, 10), (15, 15)]
    )
    sampling_method = forms.ChoiceField(
    	choices=[('sobol', 'Sobol sequences'), ('uniform', 'Uniform per dimension')]
    )
    num_samples = forms.ChoiceField(label='Configurations per race',
    	choices=[(50, 50), (100, 100), (150, 150)]
    )
    iterated_frace = forms.BooleanField(label="Iterated F-Race", required=True, initial=True)


def index(request):
    if 'username' in request.session:
        user = request.session['username']
    else:
        user = ''

    template = loader.get_template('frace/index.html')
    c = RequestContext(request, {
        'current': 'F-Race',
        'username': user,
    })
    return HttpResponse(template.render(c))

def new_job(request):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user = request.session['username']

    header = 'Upload Job'

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            jar_option = form.cleaned_data['jar_options']

            upload_path = settings.USER_DIRS + '/' + user + '_uploads'
    
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
    
            input_path = upload_path + '/' + form.cleaned_data['job_name'] + '.xml'
            jar_path = upload_path + '/' + form.cleaned_data['job_name'] + '.jar'
    
            handle_uploaded_file(request.FILES['input_file'], input_path)

            if jar_option == 'Custom':
                handle_uploaded_file(request.FILES['custom_jar_file'], jar_path)
                jar_type = 'custom'
            elif jar_option == 'Master':
                jar_path = pleiades_settings.cilib_master_path
                jar_type = 'master'
    
            output = subprocess.Popen(['java', '-jar', './Pleiades', '-u', user, '-i', input_path, '-j', jar_path, '-t', jar_type], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0];
            output = output.replace(">", "<br/>")
    
            clean_upload_dir(upload_path)
            return upload_output(request, output)
    else:
        form = UploadForm()    
    
    template = loader.get_template('frace/form.html')

    c = RequestContext(request, {
        'current': 'F-Race',
        'form': form,
        'submit': 'Upload Job',
        'header': header,
        'action': '/pleiades/upload/',
        'username': user,
    })

    return HttpResponse(template.render(c))
