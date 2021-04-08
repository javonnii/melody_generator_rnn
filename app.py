# from chapter_03_example_02 import generate 
import io 
import numpy as np
import pretty_midi
from scipy.io import wavfile 
import streamlit as st 
import math
import os
import time
import base64

import tensorflow as tf
from magenta.models.polyphony_rnn import polyphony_sequence_generator
from magenta.models.shared import sequence_generator_bundle
from note_seq import midi_io
from note_seq import notebook_utils
from note_seq.constants import DEFAULT_QUARTERS_PER_MINUTE
from note_seq.protobuf.generator_pb2 import GeneratorOptions
from note_seq.protobuf.music_pb2 import NoteSequence
from visual_midi import Plotter

st.title("Generate Polyphonic Melodies with Google Magenta")

st.subheader('By Javonnii Curry')
# upload a MIDI file
uploaded_file = st.file_uploader('Upload Primer MIDI: Must be POLYPHONIC Track', type=["mid"])

if uploaded_file is None:
    st.info("Please upload a MIDI file")
    st.stop()
    
# add sidebar slider for temperature
temperature = 1.0
temperature = st.sidebar.slider("Temp: less random < 1.0, more random > 1.0", 0.1, 2.0, step=0.01)

# add selection box
cond_primer = False 
cond_primer = st.sidebar.selectbox(
    "Activate the primer conditioning? This will use the primer to establish a certain key before the generation starts.",
    (True, False)
)

inject_primer = False
inject_primer = st.sidebar.selectbox(
    "Activates the primer injection? This will inject the primer in the generated sequence.",
    (True, False)
)

# pm upload MIDI file
midi_data = pretty_midi.PrettyMIDI(uploaded_file)



def generate(bundle_name: str,
             sequence_generator,
             generator_id: str,
             qpm: float = DEFAULT_QUARTERS_PER_MINUTE,
             condition_on_primer: bool = False,
             inject_primer_during_generation: bool = False,
             total_length_steps: int = 96,
             temperature: float = 1.0,
             beam_size: int = 1,
             branch_factor: int = 1,
             steps_per_iteration: int = 1) -> NoteSequence:
    
    
    bundle = sequence_generator_bundle.read_bundle_file(
    os.path.join("bundles", bundle_name))

    # Initialize the generator from the generator id, this need to fit the
    # bundle we downloaded before, and choose the model's configuration.
    generator_map = sequence_generator.get_generator_map()
    generator = generator_map[generator_id](checkpoint=None, bundle=bundle)
    generator.initialize()
    


    # Gets the primer sequence that is fed into the model for the generator,
    # which will generate a sequence based on this one.
    # If no primer sequence is given, the primer sequence is initialized
    # to an empty note sequence

    primer_sequence = midi_io.midi_to_note_sequence(midi_data)

        
    if primer_sequence.tempos:
        if len(primer_sequence.tempos) > 1:
            raise Exception("No support for multiple tempos")
        qpm = primer_sequence.tempos[0].qpm
        
    # Calculates the seconds per 1 step, which changes depending on the QPM value
    # (steps per quarter in generators are mostly 4)
    seconds_per_step = 60.0 / qpm / getattr(generator, "steps_per_quarter", 4)

    # Calculates the primer sequence length in steps and time by taking the
    # total time (which is the end of the last note) and finding the next step
    # start time.
    primer_sequence_length_steps = math.ceil(primer_sequence.total_time
                                            / seconds_per_step)
    primer_sequence_length_time = primer_sequence_length_steps * seconds_per_step

    # Calculates the start and the end of the primer sequence.
    # We add a negative delta to the end, because if we don't some generators
    # won't start the generation right at the beginning of the bar, they will
    # start at the next step, meaning we'll have a small gap between the primer
    # and the generated sequence.
    primer_end_adjust = (0.00001 if primer_sequence_length_time > 0 else 0)
    primer_start_time = 0
    primer_end_time = (primer_start_time
                        + primer_sequence_length_time
                        - primer_end_adjust)
        
        
    # Calculates the generation time by taking the total time and substracting
    # the primer time. The resulting generation time needs to be bigger than zero.
    generation_length_steps = total_length_steps - primer_sequence_length_steps
    if generation_length_steps <= 0:
        raise Exception("Total length in steps too small "
                        + "(" + str(total_length_steps) + ")"
                        + ", needs to be at least one bar bigger than primer "
                        + "(" + str(primer_sequence_length_steps) + ")")
    generation_length_time = generation_length_steps * seconds_per_step
        
    # Calculates the generate start and end time, the start time will contain
    # the previously added negative delta from the primer end time.
    # We remove the generation end time delta to end the generation
    # on the last bar.
    generation_start_time = primer_end_time
    generation_end_time = (generation_start_time
                            + generation_length_time
                            + primer_end_adjust)    

    generator_options = GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generator_options.args['beam_size'].int_value = beam_size
    generator_options.args['branch_factor'].int_value = branch_factor
    generator_options.args['steps_per_iteration'].int_value = steps_per_iteration
    generator_options.args['condition_on_primer'].bool_value = condition_on_primer
    generator_options.args['no_inject_primer_during_generation'].bool_value = (
        not inject_primer_during_generation)
    generator_options.generate_sections.add(
        start_time=generation_start_time,
        end_time=generation_end_time)

    # Generates the sequence, add add the time signature
    # back to the generated sequence
    sequence = generator.generate(primer_sequence, generator_options)

    # Writes the resulting midi file to the output directory, uncomment this and the markdown download below to enable MIDI download from disk. 
    date_and_time = time.strftime('%Y-%m-%d_%H%M%S')
    generator_name = str(generator.__class__).split(".")[2]
    midi_filename = "%s_%s_%s.mid" % (generator_name, generator_id,
                                        date_and_time)
    midi_path = os.path.join("output", midi_filename)
    midi_io.note_sequence_to_midi_file(sequence, midi_path)

        
    # Audio Player
    pretty_midi1 = midi_io.note_sequence_to_pretty_midi(sequence)
    audio_data = pretty_midi1.fluidsynth()
    audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767 * 0.9) # -- Normalize for 16 bit audio https://github.com/jkanner/streamlit-audio/blob/main/helper.py
    virtualfile = io.BytesIO()
    wavfile.write(virtualfile, 44100, audio_data)
    
    
    # plot MIDI
    pm = midi_io.note_sequence_to_pretty_midi(sequence)
    plotter = Plotter()
    p = plotter.show_notebook(pm)
    st.bokeh_chart(p, use_container_width=True)
    
    # download
    st.markdown(get_binary_file_downloader_html(midi_path, 'MIDI'), unsafe_allow_html=True)
    
    # MIDI to Audioplayer for download
    st.success("Play Generated MIDI")
    st.audio(virtualfile)
    st.markdown("Download audio by right-clicking on the media player")
    st.image('images/magenta_logo.png')
    st.stop()


# To download MIDI file
    
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href


def app(unused_argv):
    generate(
    "polyphony_rnn.mag",
    polyphony_sequence_generator,
    "polyphony",
    condition_on_primer=cond_primer,
    inject_primer_during_generation=False,
    temperature=temperature)
  
    return 0


if __name__ == "__main__":
  tf.compat.v1.disable_v2_behavior()
  tf.compat.v1.app.run(app)

    


