After datapreprocessing, I moved my directory to google colab to train both models.

## Key points:


Setup training
* Create two google colab notebooks, one for training set and the other for eval set. 
    * ensure that the training notebook runtime is utilizing the free gpu and that the eval notebook runtime is only on cpu.

    * mount your google drive to both notebooks

    * Start and stop the eval training once you see that the notebook has created a 'logdir' directory in the google drive at your project path. This helps so that you can watch your training and eval with tensorboard. 

    * launch tensorboard in your training set notebook 

    * Now we're ready to train our model with the training and eval sets. Here I started the training set first and then eval. 

The Melody RNN w/ attention configuration takes approx 9 hours to train. While the Melody RNN w/ base configuration takes 6 hours. 