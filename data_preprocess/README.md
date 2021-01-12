# Data Preparation

* MIDI directory is not provided because of size
* make sure you're in the magenta conda environment
```bash
conda activate magenta
```

First, change the directory to the project folder you've created and call the convet_dir_note_sequences command using the following command line

```bash
convert_dir_to_note_sequences \
--input_dir="PATH_MIDI_DIR" \
--output_file="notesequences.tfrecord"
```
This will output a bunch of "Converted MIDI" files and produce a notesequences.tfrecord as seen in the directory above.

Now, lauch the melody pipeline on the data using the following code:

```bash
melody_rnn_create_dataset \
--config="attention_rnn" \
--input="notesequences.tfrecord" \
--output_dir="sequence_examples" \
--eval_ratio=0.10
```

The sequenceExample encapulates the data that will be fed to the network during training. The statistics are useful here because the quanity of the data and quality of the data is important for the model's training.

It's important to look at the produced outputs, which tells us about the exact amount of data the network will recieve.
<hr>

