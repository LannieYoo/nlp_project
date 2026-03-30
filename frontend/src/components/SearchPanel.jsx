import { useState, useRef, useEffect, useMemo } from 'react'
import SourceCard from './SourceCard'

// ── Massive AI/ML Topic Dictionary ──────────────────────────────
// Each entry: [searchKey (lowercase), displayName, category, relatedTopics[]]
// The searchKey is used for matching user input; displayName is shown in UI.
const AI_TOPICS = [
  // ─── Core ML ───
  ['svm', 'SVM (Support Vector Machine)', 'classification', ['Kernel Methods', 'Logistic Regression', 'Hyperplane', 'Margin', 'Regularization']],
  ['support vector', 'Support Vector Machine', 'classification', ['Kernel Trick', 'Hinge Loss', 'Soft Margin', 'Dual Formulation']],
  ['logistic regression', 'Logistic Regression', 'classification', ['Linear Models', 'Sigmoid', 'Cross-Entropy', 'MLE', 'SVM']],
  ['linear regression', 'Linear Regression', 'regression', ['Least Squares', 'Ridge', 'Lasso', 'Normal Equation', 'MSE']],
  ['ridge', 'Ridge Regression', 'regression', ['L2 Regularization', 'Linear Regression', 'Bias-Variance', 'Lasso']],
  ['lasso', 'Lasso Regression', 'regression', ['L1 Regularization', 'Feature Selection', 'Sparsity', 'Ridge']],
  ['decision tree', 'Decision Tree', 'classification', ['Information Gain', 'Entropy', 'Pruning', 'Random Forest', 'Gini Index']],
  ['random forest', 'Random Forest', 'ensemble', ['Bagging', 'Decision Trees', 'Feature Importance', 'Ensemble Methods']],
  ['gradient boosting', 'Gradient Boosting', 'ensemble', ['XGBoost', 'LightGBM', 'Decision Trees', 'Ensemble Methods', 'AdaBoost']],
  ['xgboost', 'XGBoost', 'ensemble', ['Gradient Boosting', 'LightGBM', 'CatBoost', 'Regularization']],
  ['adaboost', 'AdaBoost', 'ensemble', ['Boosting', 'Weak Learners', 'Ensemble Methods', 'Gradient Boosting']],
  ['naive bayes', 'Naive Bayes', 'classification', ['Bayes Theorem', 'Probability', 'Text Classification', 'Conditional Independence']],
  ['knn', 'K-Nearest Neighbors', 'classification', ['Distance Metrics', 'Lazy Learning', 'Classification', 'Regression']],
  ['k-nearest', 'K-Nearest Neighbors', 'classification', ['Euclidean Distance', 'Curse of Dimensionality', 'KNN']],
  ['clustering', 'Clustering', 'unsupervised', ['K-Means', 'DBSCAN', 'Hierarchical', 'Silhouette Score']],
  ['k-means', 'K-Means Clustering', 'unsupervised', ['Clustering', 'Centroid', 'Elbow Method', 'DBSCAN']],
  ['kmeans', 'K-Means Clustering', 'unsupervised', ['Clustering', 'Centroid', 'Elbow Method', 'DBSCAN']],
  ['dbscan', 'DBSCAN', 'unsupervised', ['Clustering', 'Density-based', 'K-Means', 'Noise Points']],
  ['hierarchical clustering', 'Hierarchical Clustering', 'unsupervised', ['Dendrogram', 'Agglomerative', 'Divisive', 'Linkage']],
  ['pca', 'Principal Component Analysis', 'dimensionality', ['Eigenvalues', 'Eigenvectors', 'Dimensionality Reduction', 't-SNE', 'Covariance']],
  ['t-sne', 'T-SNE', 'dimensionality', ['Visualization', 'PCA', 'UMAP', 'Dimensionality Reduction']],
  ['umap', 'UMAP', 'dimensionality', ['t-SNE', 'PCA', 'Manifold Learning', 'Visualization']],
  ['feature selection', 'Feature Selection', 'preprocessing', ['Lasso', 'Mutual Information', 'PCA', 'Feature Engineering']],
  ['feature engineering', 'Feature Engineering', 'preprocessing', ['Feature Selection', 'Encoding', 'Normalization', 'Domain Knowledge']],
  ['cross-validation', 'Cross-Validation', 'evaluation', ['K-Fold', 'Stratified', 'Model Selection', 'Overfitting']],
  ['cross validation', 'Cross-Validation', 'evaluation', ['K-Fold', 'Stratified', 'Model Selection', 'Overfitting']],
  ['overfitting', 'Overfitting', 'fundamentals', ['Regularization', 'Cross-Validation', 'Bias-Variance', 'Dropout']],
  ['underfitting', 'Underfitting', 'fundamentals', ['Model Complexity', 'Bias', 'Feature Engineering', 'Overfitting']],
  ['bias variance', 'Bias-Variance Tradeoff', 'fundamentals', ['Overfitting', 'Underfitting', 'Model Complexity', 'Regularization']],
  ['ensemble', 'Ensemble Methods', 'ensemble', ['Bagging', 'Boosting', 'Stacking', 'Random Forest', 'Voting']],
  ['bagging', 'Bagging', 'ensemble', ['Bootstrap', 'Random Forest', 'Ensemble', 'Variance Reduction']],
  ['boosting', 'Boosting', 'ensemble', ['AdaBoost', 'Gradient Boosting', 'XGBoost', 'Ensemble']],

  // ─── Deep Learning ───
  ['neural network', 'Neural Network', 'deep learning', ['Layers', 'Activation Functions', 'Backpropagation', 'Deep Learning']],
  ['deep learning', 'Deep Learning', 'deep learning', ['Neural Networks', 'CNN', 'RNN', 'Transformer', 'GPU']],
  ['cnn', 'Convolutional Neural Network', 'deep learning', ['Convolution', 'Pooling', 'ResNet', 'Image Classification']],
  ['convolutional', 'Convolutional Neural Network', 'deep learning', ['Filters', 'Stride', 'Padding', 'Feature Maps', 'Pooling']],
  ['rnn', 'Recurrent Neural Network', 'deep learning', ['LSTM', 'GRU', 'Sequence Modeling', 'Vanishing Gradient']],
  ['recurrent', 'Recurrent Neural Network', 'deep learning', ['LSTM', 'GRU', 'Time Series', 'Sequence Modeling']],
  ['lstm', 'LSTM', 'deep learning', ['RNN', 'GRU', 'Gates', 'Long-range Dependencies', 'Forget Gate']],
  ['gru', 'GRU', 'deep learning', ['LSTM', 'RNN', 'Reset Gate', 'Update Gate']],
  ['transformer', 'Transformer', 'deep learning', ['Self-Attention', 'BERT', 'GPT', 'Positional Encoding', 'Multi-Head Attention']],
  ['attention', 'Attention Mechanism', 'deep learning', ['Self-Attention', 'Multi-Head', 'Transformer', 'Seq2Seq', 'Cross-Attention']],
  ['self-attention', 'Self-Attention', 'deep learning', ['Transformer', 'Multi-Head Attention', 'Query Key Value']],
  ['multi-head', 'Multi-Head Attention', 'deep learning', ['Transformer', 'Self-Attention', 'Parallel Heads']],
  ['resnet', 'ResNet', 'deep learning', ['Skip Connection', 'CNN', 'Residual Learning', 'VGG', 'ImageNet']],
  ['vgg', 'VGG Network', 'deep learning', ['CNN', 'ResNet', 'Deep Features', 'Image Classification']],
  ['inception', 'Inception Network', 'deep learning', ['GoogLeNet', 'CNN', 'Multi-scale Features', 'ResNet']],
  ['autoencoder', 'Autoencoder', 'deep learning', ['Encoder-Decoder', 'VAE', 'Dimensionality Reduction', 'Representation Learning']],
  ['vae', 'Variational Autoencoder', 'deep learning', ['Autoencoder', 'Latent Space', 'Generative Model', 'KL Divergence']],
  ['gan', 'Generative Adversarial Network', 'deep learning', ['Generator', 'Discriminator', 'Mode Collapse', 'Image Generation']],
  ['generative adversarial', 'GAN', 'deep learning', ['Generator', 'Discriminator', 'Wasserstein', 'StyleGAN']],
  ['diffusion', 'Diffusion Model', 'deep learning', ['Image Generation', 'Denoising', 'DDPM', 'Stable Diffusion', 'GAN']],
  ['dropout', 'Dropout', 'regularization', ['Regularization', 'Overfitting', 'Ensemble Effect', 'Batch Normalization']],
  ['batch normalization', 'Batch Normalization', 'deep learning', ['Layer Normalization', 'Training Stability', 'Internal Covariate Shift']],
  ['layer normalization', 'Layer Normalization', 'deep learning', ['Batch Normalization', 'Transformer', 'RNN']],
  ['activation', 'Activation Function', 'deep learning', ['ReLU', 'Sigmoid', 'Tanh', 'Softmax', 'GELU']],
  ['relu', 'ReLU', 'deep learning', ['Activation', 'Leaky ReLU', 'GELU', 'Vanishing Gradient']],
  ['sigmoid', 'Sigmoid Function', 'deep learning', ['Activation', 'Logistic Regression', 'Binary Classification']],
  ['softmax', 'Softmax Function', 'deep learning', ['Probability', 'Classification', 'Cross-Entropy', 'Temperature']],
  ['pooling', 'Pooling Layer', 'deep learning', ['CNN', 'Max Pooling', 'Average Pooling', 'Feature Reduction']],
  ['skip connection', 'Skip Connection', 'deep learning', ['ResNet', 'Residual Learning', 'Gradient Flow']],

  // ─── Optimization ───
  ['gradient descent', 'Gradient Descent', 'optimization', ['SGD', 'Adam', 'Learning Rate', 'Backpropagation']],
  ['gradient', 'Gradient Descent', 'optimization', ['SGD', 'Momentum', 'Adam', 'Learning Rate']],
  ['sgd', 'Stochastic Gradient Descent', 'optimization', ['Mini-batch', 'Adam', 'Momentum', 'Learning Rate']],
  ['adam', 'Adam Optimizer', 'optimization', ['SGD', 'RMSprop', 'Learning Rate', 'Momentum', 'AdamW']],
  ['rmsprop', 'RMSprop', 'optimization', ['Adam', 'SGD', 'Adaptive Learning Rate']],
  ['momentum', 'Momentum', 'optimization', ['SGD', 'Nesterov', 'Gradient Descent', 'Convergence']],
  ['learning rate', 'Learning Rate', 'optimization', ['Scheduler', 'Warm-up', 'Decay', 'Adam', 'SGD']],
  ['backpropagation', 'Backpropagation', 'optimization', ['Chain Rule', 'Gradient Descent', 'Automatic Differentiation']],
  ['loss function', 'Loss Function', 'optimization', ['Cross-Entropy', 'MSE', 'Hinge Loss', 'Focal Loss']],
  ['cross-entropy', 'Cross-Entropy Loss', 'optimization', ['Loss Function', 'Softmax', 'Classification', 'KL Divergence']],
  ['mse', 'Mean Squared Error', 'optimization', ['Loss Function', 'Regression', 'MAE', 'RMSE']],
  ['vanishing gradient', 'Vanishing Gradient Problem', 'optimization', ['LSTM', 'ReLU', 'Residual Networks', 'Batch Normalization']],
  ['weight initialization', 'Weight Initialization', 'optimization', ['Xavier', 'He Initialization', 'Neural Networks']],
  ['hyperparameter', 'Hyperparameter Tuning', 'optimization', ['Grid Search', 'Random Search', 'Bayesian Optimization']],

  // ─── NLP ───
  ['nlp', 'Natural Language Processing', 'nlp', ['Tokenization', 'Word Embeddings', 'Transformers', 'BERT', 'GPT']],
  ['natural language', 'Natural Language Processing', 'nlp', ['Tokenization', 'Parsing', 'Sentiment Analysis', 'NER']],
  ['bert', 'BERT', 'nlp', ['Masked LM', 'Fine-tuning', 'Transformer', 'Pre-training', 'NLP']],
  ['gpt', 'GPT', 'nlp', ['Language Model', 'Transformer', 'Autoregressive', 'BERT', 'Fine-tuning']],
  ['word2vec', 'Word2Vec', 'nlp', ['Word Embeddings', 'Skip-gram', 'CBOW', 'GloVe']],
  ['word embedding', 'Word Embeddings', 'nlp', ['Word2Vec', 'GloVe', 'FastText', 'Contextual Embedding']],
  ['embedding', 'Embeddings', 'nlp', ['Word2Vec', 'GloVe', 'Positional Encoding', 'Representation']],
  ['glove', 'GloVe', 'nlp', ['Word2Vec', 'Word Embeddings', 'Co-occurrence', 'NLP']],
  ['tokenization', 'Tokenization', 'nlp', ['BPE', 'WordPiece', 'SentencePiece', 'NLP']],
  ['tf-idf', 'TF-IDF', 'nlp', ['Information Retrieval', 'Term Frequency', 'Document Similarity']],
  ['tfidf', 'TF-IDF', 'nlp', ['Information Retrieval', 'Term Frequency', 'Document Similarity']],
  ['sentiment analysis', 'Sentiment Analysis', 'nlp', ['Text Classification', 'NLP', 'BERT', 'Opinion Mining']],
  ['named entity', 'Named Entity Recognition', 'nlp', ['NLP', 'Sequence Labeling', 'CRF', 'BERT']],
  ['machine translation', 'Machine Translation', 'nlp', ['Seq2Seq', 'Attention', 'Transformer', 'BLEU']],
  ['language model', 'Language Model', 'nlp', ['GPT', 'BERT', 'Perplexity', 'Autoregressive', 'Masked LM']],
  ['seq2seq', 'Sequence-to-Sequence', 'nlp', ['Encoder-Decoder', 'Attention', 'Machine Translation', 'Transformer']],
  ['text classification', 'Text Classification', 'nlp', ['NLP', 'Sentiment', 'BERT', 'Naive Bayes']],

  // ─── Computer Vision ───
  ['computer vision', 'Computer Vision', 'vision', ['CNN', 'Object Detection', 'Image Segmentation', 'Feature Extraction']],
  ['object detection', 'Object Detection', 'vision', ['YOLO', 'R-CNN', 'Anchor Boxes', 'IoU', 'NMS']],
  ['yolo', 'YOLO', 'vision', ['Object Detection', 'Real-time', 'Anchor Boxes', 'R-CNN']],
  ['image segmentation', 'Image Segmentation', 'vision', ['U-Net', 'Semantic', 'Instance', 'Pixel Classification']],
  ['image classification', 'Image Classification', 'vision', ['CNN', 'ResNet', 'ImageNet', 'Transfer Learning']],
  ['data augmentation', 'Data Augmentation', 'vision', ['Training', 'Overfitting', 'Regularization', 'Image Transform']],
  ['face recognition', 'Face Recognition', 'vision', ['CNN', 'FaceNet', 'Triplet Loss', 'Siamese Network']],
  ['optical flow', 'Optical Flow', 'vision', ['Motion Estimation', 'Video Analysis', 'Lucas-Kanade']],

  // ─── Reinforcement Learning ───
  ['reinforcement learning', 'Reinforcement Learning', 'rl', ['Q-Learning', 'Policy Gradient', 'Reward', 'MDP', 'DQN']],
  ['reinforcement', 'Reinforcement Learning', 'rl', ['Q-Learning', 'Policy Gradient', 'Reward', 'MDP']],
  ['q-learning', 'Q-Learning', 'rl', ['RL', 'DQN', 'Bellman Equation', 'Value Function']],
  ['policy gradient', 'Policy Gradient', 'rl', ['REINFORCE', 'Actor-Critic', 'PPO', 'RL']],
  ['dqn', 'Deep Q-Network', 'rl', ['Q-Learning', 'Experience Replay', 'Target Network', 'RL']],
  ['ppo', 'PPO', 'rl', ['Policy Gradient', 'Actor-Critic', 'Clipping', 'RL']],
  ['markov', 'Markov Decision Process', 'rl', ['RL', 'State Space', 'Transition', 'Reward']],
  ['reward', 'Reward Function', 'rl', ['RL', 'Sparse Reward', 'Reward Shaping', 'MDP']],

  // ─── Bayesian / Probabilistic ───
  ['bayesian', 'Bayesian Methods', 'probabilistic', ['Prior', 'Posterior', 'Bayes Theorem', 'MCMC', 'Inference']],
  ['bayes', 'Bayes Theorem', 'probabilistic', ['Bayesian', 'Prior', 'Posterior', 'Likelihood']],
  ['probability', 'Probability Theory', 'probabilistic', ['Random Variable', 'Distribution', 'Bayes', 'Expectation']],
  ['gaussian', 'Gaussian Distribution', 'probabilistic', ['Normal Distribution', 'GMM', 'Central Limit Theorem']],
  ['mle', 'Maximum Likelihood Estimation', 'probabilistic', ['MLE', 'MAP', 'Log-Likelihood', 'Parameter Estimation']],
  ['maximum likelihood', 'Maximum Likelihood Estimation', 'probabilistic', ['MLE', 'MAP', 'Bayesian', 'Parameter']],
  ['map estimation', 'MAP Estimation', 'probabilistic', ['MLE', 'Bayesian', 'Prior', 'Posterior']],
  ['em algorithm', 'EM Algorithm', 'probabilistic', ['Gaussian Mixture', 'Clustering', 'Latent Variables', 'MLE']],
  ['expectation maximization', 'EM Algorithm', 'probabilistic', ['GMM', 'Clustering', 'Latent', 'K-Means']],
  ['mcmc', 'MCMC', 'probabilistic', ['Gibbs Sampling', 'Metropolis-Hastings', 'Bayesian', 'Sampling']],
  ['hidden markov', 'Hidden Markov Model', 'probabilistic', ['Viterbi', 'Baum-Welch', 'Sequence Modeling']],
  ['hmm', 'Hidden Markov Model', 'probabilistic', ['Viterbi', 'Baum-Welch', 'Sequence Modeling']],
  ['graphical model', 'Graphical Model', 'probabilistic', ['Bayesian Network', 'MRF', 'Factor Graph']],

  // ─── Regularization / Training ───
  ['regularization', 'Regularization', 'training', ['L1', 'L2', 'Dropout', 'Weight Decay', 'Early Stopping']],
  ['l1 regularization', 'L1 Regularization', 'training', ['Lasso', 'Sparsity', 'Feature Selection']],
  ['l2 regularization', 'L2 Regularization', 'training', ['Ridge', 'Weight Decay', 'Norm Penalty']],
  ['early stopping', 'Early Stopping', 'training', ['Overfitting', 'Validation Loss', 'Regularization']],
  ['weight decay', 'Weight Decay', 'training', ['L2 Regularization', 'AdamW', 'Overfitting']],
  ['data preprocessing', 'Data Preprocessing', 'training', ['Normalization', 'Standardization', 'Feature Scaling', 'Missing Data']],
  ['normalization', 'Normalization', 'training', ['Min-Max', 'Z-score', 'Batch Normalization', 'Standardization']],
  ['transfer learning', 'Transfer Learning', 'training', ['Fine-tuning', 'Pre-training', 'Domain Adaptation', 'CNN']],
  ['fine-tuning', 'Fine-tuning', 'training', ['Transfer Learning', 'Pre-training', 'BERT', 'Domain Adaptation']],
  ['curriculum learning', 'Curriculum Learning', 'training', ['Training Strategy', 'Easy-to-Hard', 'Self-paced']],
  ['knowledge distillation', 'Knowledge Distillation', 'training', ['Model Compression', 'Teacher-Student', 'Pruning']],

  // ─── Metrics / Evaluation ───
  ['accuracy', 'Accuracy', 'evaluation', ['Precision', 'Recall', 'F1-Score', 'Confusion Matrix']],
  ['precision', 'Precision', 'evaluation', ['Recall', 'F1-Score', 'Accuracy', 'True Positive']],
  ['recall', 'Recall', 'evaluation', ['Precision', 'F1-Score', 'Sensitivity', 'True Positive']],
  ['f1', 'F1-Score', 'evaluation', ['Precision', 'Recall', 'Accuracy', 'Harmonic Mean']],
  ['roc', 'ROC Curve', 'evaluation', ['AUC', 'True Positive Rate', 'False Positive Rate']],
  ['auc', 'AUC', 'evaluation', ['ROC', 'Classification', 'Threshold', 'Performance']],
  ['confusion matrix', 'Confusion Matrix', 'evaluation', ['Accuracy', 'Precision', 'Recall', 'Classification']],
  ['perplexity', 'Perplexity', 'evaluation', ['Language Model', 'NLP', 'Probability', 'Cross-Entropy']],
  ['bleu', 'BLEU Score', 'evaluation', ['Machine Translation', 'NLP', 'Evaluation Metric']],

  // ─── Other Advanced Topics ───
  ['graph neural', 'Graph Neural Network', 'advanced', ['GCN', 'Message Passing', 'Graph Convolution', 'Node Embedding']],
  ['gcn', 'Graph Convolutional Network', 'advanced', ['GNN', 'Graph Learning', 'Node Classification']],
  ['meta-learning', 'Meta-Learning', 'advanced', ['Few-shot', 'MAML', 'Learning to Learn']],
  ['few-shot', 'Few-Shot Learning', 'advanced', ['Meta-Learning', 'Zero-Shot', 'Prototypical']],
  ['contrastive learning', 'Contrastive Learning', 'advanced', ['SimCLR', 'Self-supervised', 'Representation']],
  ['self-supervised', 'Self-Supervised Learning', 'advanced', ['Contrastive', 'Pretext Task', 'BERT', 'SimCLR']],
  ['federated learning', 'Federated Learning', 'advanced', ['Privacy', 'Distributed', 'Aggregation']],
  ['neural architecture', 'Neural Architecture Search', 'advanced', ['AutoML', 'NAS', 'Model Design']],
  ['automl', 'AutoML', 'advanced', ['NAS', 'Hyperparameter', 'Automated ML']],
  ['explainability', 'Explainability (XAI)', 'advanced', ['SHAP', 'LIME', 'Interpretability', 'Feature Importance']],
  ['interpretability', 'Interpretability', 'advanced', ['Explainability', 'SHAP', 'LIME', 'Attention Maps']],
  ['fairness', 'Fairness in ML', 'advanced', ['Bias', 'Ethics', 'Discrimination', 'Responsible AI']],
  ['multi-task', 'Multi-Task Learning', 'advanced', ['Shared Layers', 'Transfer Learning', 'Joint Training']],
  ['continual learning', 'Continual Learning', 'advanced', ['Catastrophic Forgetting', 'Lifelong Learning', 'Replay']],
  ['domain adaptation', 'Domain Adaptation', 'advanced', ['Transfer Learning', 'Distribution Shift', 'UDA']],
  ['information theory', 'Information Theory', 'fundamentals', ['Entropy', 'KL Divergence', 'Mutual Information', 'Cross-Entropy']],
  ['entropy', 'Entropy', 'fundamentals', ['Information Theory', 'Decision Trees', 'Cross-Entropy', 'KL Divergence']],
  ['kl divergence', 'KL Divergence', 'fundamentals', ['Entropy', 'VAE', 'Probability', 'Cross-Entropy']],
  ['matrix factorization', 'Matrix Factorization', 'fundamentals', ['SVD', 'Recommendation', 'PCA', 'Low-Rank']],
  ['svd', 'Singular Value Decomposition', 'fundamentals', ['Matrix Factorization', 'PCA', 'Dimensionality Reduction']],
  ['convex optimization', 'Convex Optimization', 'optimization', ['Gradient Descent', 'Lagrangian', 'Duality', 'KKT']],
  ['model compression', 'Model Compression', 'advanced', ['Pruning', 'Quantization', 'Distillation', 'Mobile']],
  ['pruning', 'Network Pruning', 'advanced', ['Model Compression', 'Sparsity', 'Knowledge Distillation']],
  ['quantization', 'Quantization', 'advanced', ['Model Compression', 'INT8', 'Low-Precision', 'Inference']],
  ['recommendation', 'Recommendation System', 'applications', ['Collaborative Filtering', 'Content-based', 'Matrix Factorization']],
  ['anomaly detection', 'Anomaly Detection', 'applications', ['Outlier', 'Autoencoder', 'Isolation Forest', 'One-Class SVM']],
  ['time series', 'Time Series Analysis', 'applications', ['LSTM', 'ARIMA', 'Forecasting', 'RNN', 'Temporal']],
  ['speech recognition', 'Speech Recognition', 'applications', ['ASR', 'CTC', 'Wav2Vec', 'Audio']],
  ['generative model', 'Generative Model', 'deep learning', ['GAN', 'VAE', 'Diffusion', 'Autoregressive']],

  // ─── Neural Network Layers & Components ───
  ['mlp', 'MLP (Multi-Layer Perceptron)', 'deep learning', ['Feedforward', 'Layers', 'Activation', 'Neural Network']],
  ['multi-layer perceptron', 'MLP (Multi-Layer Perceptron)', 'deep learning', ['Feedforward', 'Hidden Layers', 'Activation']],
  ['perceptron', 'Perceptron', 'deep learning', ['Linear Classifier', 'Neuron', 'MLP', 'Activation']],
  ['maxpool', 'Max Pooling', 'deep learning', ['CNN', 'Pooling', 'Feature Reduction', 'Stride']],
  ['max pooling', 'Max Pooling', 'deep learning', ['CNN', 'Average Pooling', 'Stride', 'Downsampling']],
  ['average pooling', 'Average Pooling', 'deep learning', ['CNN', 'Max Pooling', 'Global Average Pooling']],
  ['global average pooling', 'Global Average Pooling', 'deep learning', ['CNN', 'Feature Aggregation', 'Flatten']],
  ['flatten', 'Flatten Layer', 'deep learning', ['CNN', 'Dense Layer', 'Reshape', 'MLP']],
  ['dense layer', 'Dense Layer (Fully Connected)', 'deep learning', ['MLP', 'Weights', 'Bias', 'Linear']],
  ['fully connected', 'Fully Connected Layer', 'deep learning', ['Dense', 'MLP', 'Neural Network', 'Weights']],
  ['convolution layer', 'Convolution Layer', 'deep learning', ['CNN', 'Filters', 'Kernel', 'Feature Maps']],
  ['depthwise convolution', 'Depthwise Separable Convolution', 'deep learning', ['MobileNet', 'Efficient CNN', 'Lightweight']],
  ['deconvolution', 'Transposed Convolution', 'deep learning', ['Upsampling', 'Decoder', 'Segmentation']],
  ['upsampling', 'Upsampling', 'deep learning', ['Transposed Convolution', 'Interpolation', 'Decoder']],
  ['residual block', 'Residual Block', 'deep learning', ['ResNet', 'Skip Connection', 'Identity Mapping']],
  ['bottleneck', 'Bottleneck Layer', 'deep learning', ['ResNet', 'Autoencoder', 'Dimensionality Reduction']],
  ['embedding layer', 'Embedding Layer', 'deep learning', ['Word Embeddings', 'Lookup Table', 'NLP', 'Representation']],

  // ─── Activation Functions ───
  ['tanh', 'Tanh Activation', 'deep learning', ['Activation', 'Sigmoid', 'ReLU', 'Hyperbolic Tangent']],
  ['leaky relu', 'Leaky ReLU', 'deep learning', ['ReLU', 'Activation', 'Dying ReLU', 'PReLU']],
  ['elu', 'ELU', 'deep learning', ['Activation', 'ReLU', 'SELU', 'Smooth']],
  ['selu', 'SELU', 'deep learning', ['Activation', 'Self-Normalizing', 'ELU']],
  ['gelu', 'GELU', 'deep learning', ['Activation', 'Transformer', 'BERT', 'Smooth ReLU']],
  ['swish', 'Swish Activation', 'deep learning', ['Activation', 'ReLU', 'Self-gated', 'EfficientNet']],
  ['mish', 'Mish Activation', 'deep learning', ['Activation', 'Smooth', 'YOLOv4']],

  // ─── CNN Architectures ───
  ['alexnet', 'AlexNet', 'deep learning', ['CNN', 'ImageNet', 'ReLU', 'GPU Training']],
  ['lenet', 'LeNet', 'deep learning', ['CNN', 'Handwriting', 'MNIST', 'Convolution']],
  ['mobilenet', 'MobileNet', 'deep learning', ['Depthwise Convolution', 'Lightweight', 'Mobile', 'Efficient']],
  ['efficientnet', 'EfficientNet', 'deep learning', ['Scaling', 'CNN', 'Compound Scaling', 'NAS']],
  ['densenet', 'DenseNet', 'deep learning', ['Dense Connections', 'Feature Reuse', 'CNN', 'ResNet']],
  ['squeezenet', 'SqueezeNet', 'deep learning', ['Lightweight', 'Fire Module', 'CNN', 'Compression']],
  ['unet', 'U-Net', 'deep learning', ['Segmentation', 'Encoder-Decoder', 'Skip Connection', 'Medical Imaging']],
  ['u-net', 'U-Net', 'deep learning', ['Segmentation', 'Encoder-Decoder', 'Medical Imaging']],

  // ─── Transformer Variants ───
  ['gpt', 'GPT', 'nlp', ['Language Model', 'Transformer', 'Autoregressive', 'BERT', 'Fine-tuning']],
  ['t5', 'T5 (Text-to-Text Transformer)', 'nlp', ['Transformer', 'Pre-training', 'Encoder-Decoder', 'NLP']],
  ['xlnet', 'XLNet', 'nlp', ['Transformer', 'Permutation LM', 'BERT', 'Autoregressive']],
  ['roberta', 'RoBERTa', 'nlp', ['BERT', 'Pre-training', 'Dynamic Masking', 'NLP']],
  ['albert', 'ALBERT', 'nlp', ['BERT', 'Parameter Sharing', 'Lightweight', 'NLP']],
  ['distilbert', 'DistilBERT', 'nlp', ['BERT', 'Distillation', 'Lightweight', 'NLP']],
  ['electra', 'ELECTRA', 'nlp', ['Pre-training', 'Replaced Token Detection', 'BERT']],
  ['vision transformer', 'Vision Transformer (ViT)', 'deep learning', ['Transformer', 'Image Classification', 'Patch Embedding', 'CNN']],
  ['vit', 'Vision Transformer (ViT)', 'deep learning', ['Transformer', 'Image Patches', 'Self-Attention', 'CNN']],
  ['swin', 'Swin Transformer', 'deep learning', ['Shifted Window', 'Vision Transformer', 'Hierarchical']],
  ['detr', 'DETR', 'deep learning', ['Object Detection', 'Transformer', 'Set Prediction', 'YOLO']],

  // ─── Object Detection ───
  ['r-cnn', 'R-CNN', 'vision', ['Object Detection', 'Region Proposals', 'CNN', 'Faster R-CNN']],
  ['faster r-cnn', 'Faster R-CNN', 'vision', ['Object Detection', 'RPN', 'Anchor Boxes', 'R-CNN']],
  ['mask r-cnn', 'Mask R-CNN', 'vision', ['Instance Segmentation', 'Object Detection', 'Faster R-CNN']],
  ['ssd', 'SSD (Single Shot Detector)', 'vision', ['Object Detection', 'Multi-scale', 'YOLO', 'Anchor']],
  ['anchor box', 'Anchor Boxes', 'vision', ['Object Detection', 'YOLO', 'SSD', 'Aspect Ratio']],
  ['iou', 'IoU (Intersection over Union)', 'vision', ['Object Detection', 'Evaluation', 'Bounding Box', 'NMS']],
  ['nms', 'Non-Maximum Suppression', 'vision', ['Object Detection', 'Bounding Box', 'IoU', 'Post-processing']],
  ['fpn', 'Feature Pyramid Network', 'vision', ['Multi-scale', 'Object Detection', 'CNN', 'FPN']],

  // ─── Loss Functions ───
  ['hinge loss', 'Hinge Loss', 'optimization', ['SVM', 'Margin', 'Classification', 'Loss Function']],
  ['focal loss', 'Focal Loss', 'optimization', ['Class Imbalance', 'Object Detection', 'Cross-Entropy']],
  ['triplet loss', 'Triplet Loss', 'optimization', ['Metric Learning', 'Embedding', 'Face Recognition', 'Contrastive']],
  ['contrastive loss', 'Contrastive Loss', 'optimization', ['Metric Learning', 'Siamese Network', 'Embedding']],
  ['dice loss', 'Dice Loss', 'optimization', ['Segmentation', 'IoU', 'Medical Imaging']],
  ['bce', 'Binary Cross-Entropy', 'optimization', ['Loss Function', 'Binary Classification', 'Sigmoid']],
  ['mae', 'Mean Absolute Error', 'optimization', ['Loss Function', 'Regression', 'MSE', 'Robustness']],
  ['huber loss', 'Huber Loss', 'optimization', ['Loss Function', 'Regression', 'MSE', 'MAE']],

  // ─── Math / Linear Algebra ───
  ['eigenvalue', 'Eigenvalues and Eigenvectors', 'math', ['PCA', 'Linear Algebra', 'Matrix', 'SVD']],
  ['covariance', 'Covariance Matrix', 'math', ['PCA', 'Correlation', 'Gaussian', 'Statistics']],
  ['jacobian', 'Jacobian Matrix', 'math', ['Gradient', 'Backpropagation', 'Partial Derivatives']],
  ['hessian', 'Hessian Matrix', 'math', ['Second Order', 'Optimization', 'Curvature', 'Newton Method']],
  ['dot product', 'Dot Product', 'math', ['Attention', 'Similarity', 'Cosine', 'Linear Algebra']],
  ['cosine similarity', 'Cosine Similarity', 'math', ['Similarity', 'Embedding', 'Distance Metric', 'NLP']],
  ['euclidean distance', 'Euclidean Distance', 'math', ['KNN', 'Clustering', 'Distance Metric', 'L2 Norm']],
  ['manhattan distance', 'Manhattan Distance', 'math', ['L1 Norm', 'Distance Metric', 'KNN']],
  ['norm', 'Norm (L1, L2)', 'math', ['Regularization', 'Distance', 'Vector', 'Normalization']],
  ['tensor', 'Tensor', 'math', ['PyTorch', 'TensorFlow', 'Multi-dimensional Array', 'GPU']],
  ['matrix multiplication', 'Matrix Multiplication', 'math', ['Linear Algebra', 'Neural Networks', 'GPU', 'Attention']],

  // ─── Training Techniques ───
  ['mini-batch', 'Mini-Batch Training', 'training', ['Batch Size', 'SGD', 'Gradient Descent', 'GPU']],
  ['batch size', 'Batch Size', 'training', ['Mini-Batch', 'Training', 'GPU Memory', 'Convergence']],
  ['epoch', 'Epoch', 'training', ['Training', 'Iteration', 'Batch', 'Convergence']],
  ['warmup', 'Learning Rate Warmup', 'training', ['Learning Rate', 'Transformer', 'Scheduler', 'Training']],
  ['lr scheduler', 'Learning Rate Scheduler', 'training', ['Cosine Annealing', 'Step Decay', 'Warmup']],
  ['cosine annealing', 'Cosine Annealing', 'training', ['LR Scheduler', 'Learning Rate', 'Cyclical LR']],
  ['gradient clipping', 'Gradient Clipping', 'training', ['Exploding Gradient', 'RNN', 'Training Stability']],
  ['label smoothing', 'Label Smoothing', 'training', ['Regularization', 'Cross-Entropy', 'Overconfidence']],
  ['mixed precision', 'Mixed Precision Training', 'training', ['FP16', 'GPU', 'Training Speed', 'Memory']],
  ['distributed training', 'Distributed Training', 'training', ['Data Parallel', 'Model Parallel', 'GPU', 'Multi-node']],
  ['data parallel', 'Data Parallelism', 'training', ['Distributed', 'GPU', 'Batch Split', 'Synchronization']],
  ['checkpoint', 'Model Checkpointing', 'training', ['Saving', 'Resume Training', 'Best Model']],
  ['early stopping', 'Early Stopping', 'training', ['Overfitting', 'Validation Loss', 'Regularization', 'Patience']],
  ['weight initialization', 'Weight Initialization', 'training', ['Xavier', 'He', 'Kaiming', 'Random']],
  ['xavier', 'Xavier Initialization', 'training', ['Weight Init', 'Glorot', 'Sigmoid', 'Tanh']],
  ['he initialization', 'He Initialization', 'training', ['Weight Init', 'Kaiming', 'ReLU', 'Deep Networks']],

  // ─── Frameworks / Tools ───
  ['pytorch', 'PyTorch', 'framework', ['Deep Learning', 'Tensor', 'Autograd', 'GPU']],
  ['tensorflow', 'TensorFlow', 'framework', ['Deep Learning', 'Keras', 'GPU', 'Production']],
  ['keras', 'Keras', 'framework', ['TensorFlow', 'High-level API', 'Layers', 'Model']],
  ['scikit-learn', 'Scikit-learn', 'framework', ['ML Library', 'Classification', 'Regression', 'Python']],
  ['sklearn', 'Scikit-learn', 'framework', ['ML Library', 'Pipeline', 'Preprocessing', 'Model Selection']],
  ['huggingface', 'Hugging Face', 'framework', ['Transformers', 'NLP', 'Pre-trained Models', 'BERT']],
  ['onnx', 'ONNX', 'framework', ['Model Export', 'Interoperability', 'Inference', 'Deployment']],
  ['tensorrt', 'TensorRT', 'framework', ['Inference', 'NVIDIA', 'Optimization', 'Deployment']],

  // ─── Generative AI ───
  ['stable diffusion', 'Stable Diffusion', 'generative', ['Image Generation', 'Diffusion', 'Text-to-Image', 'Latent']],
  ['dall-e', 'DALL-E', 'generative', ['Image Generation', 'Text-to-Image', 'OpenAI', 'CLIP']],
  ['midjourney', 'Midjourney', 'generative', ['Image Generation', 'Text-to-Image', 'AI Art']],
  ['clip', 'CLIP', 'generative', ['Vision-Language', 'Contrastive', 'Zero-Shot', 'OpenAI']],
  ['rlhf', 'RLHF', 'generative', ['Reinforcement Learning', 'Human Feedback', 'GPT', 'Alignment']],
  ['prompt engineering', 'Prompt Engineering', 'generative', ['LLM', 'GPT', 'In-context Learning', 'Few-shot']],
  ['rag', 'RAG (Retrieval Augmented Generation)', 'generative', ['LLM', 'Information Retrieval', 'Grounding', 'Context']],
  ['llm', 'Large Language Model', 'generative', ['GPT', 'BERT', 'Transformer', 'Pre-training', 'Scaling']],
  ['large language model', 'Large Language Model', 'generative', ['GPT', 'Scaling Laws', 'Transformer', 'Emergent']],
  ['chatgpt', 'ChatGPT', 'generative', ['GPT', 'RLHF', 'Dialogue', 'LLM']],
  ['in-context learning', 'In-Context Learning', 'generative', ['LLM', 'Few-shot', 'Prompt', 'GPT']],
  ['chain of thought', 'Chain-of-Thought Prompting', 'generative', ['LLM', 'Reasoning', 'Prompt Engineering']],
  ['lora', 'LoRA', 'generative', ['Fine-tuning', 'Parameter Efficient', 'Low-Rank', 'LLM']],

  // ─── Statistical ML ───
  ['gaussian mixture', 'Gaussian Mixture Model', 'probabilistic', ['EM Algorithm', 'Clustering', 'Density Estimation']],
  ['gmm', 'Gaussian Mixture Model', 'probabilistic', ['EM', 'Clustering', 'Gaussian', 'Density']],
  ['kernel method', 'Kernel Methods', 'classification', ['SVM', 'Kernel Trick', 'RBF', 'Polynomial']],
  ['kernel trick', 'Kernel Trick', 'classification', ['SVM', 'RBF Kernel', 'Feature Space', 'Non-linear']],
  ['rbf', 'RBF Kernel', 'classification', ['SVM', 'Gaussian Kernel', 'Kernel Methods']],
  ['isolation forest', 'Isolation Forest', 'applications', ['Anomaly Detection', 'Outlier', 'Ensemble', 'Random']],
  ['one-class svm', 'One-Class SVM', 'applications', ['Anomaly Detection', 'Novelty Detection', 'SVM']],
  ['crf', 'Conditional Random Field', 'probabilistic', ['Sequence Labeling', 'NER', 'HMM', 'Structured Prediction']],

  // ─── Data & Preprocessing ───
  ['one-hot encoding', 'One-Hot Encoding', 'preprocessing', ['Categorical', 'Encoding', 'Feature Engineering']],
  ['label encoding', 'Label Encoding', 'preprocessing', ['Categorical', 'Ordinal', 'One-Hot']],
  ['standardization', 'Standardization', 'preprocessing', ['Z-Score', 'Normalization', 'Mean', 'Variance']],
  ['min-max scaling', 'Min-Max Scaling', 'preprocessing', ['Normalization', 'Feature Scaling', 'Range']],
  ['imputation', 'Missing Value Imputation', 'preprocessing', ['Missing Data', 'Mean', 'Median', 'KNN Imputer']],
  ['class imbalance', 'Class Imbalance', 'preprocessing', ['SMOTE', 'Oversampling', 'Undersampling', 'Focal Loss']],
  ['smote', 'SMOTE', 'preprocessing', ['Oversampling', 'Class Imbalance', 'Synthetic Data']],
  ['train test split', 'Train-Test Split', 'preprocessing', ['Cross-Validation', 'Evaluation', 'Holdout']],
  ['stratified sampling', 'Stratified Sampling', 'preprocessing', ['Cross-Validation', 'Class Balance', 'Split']],

  // ─── Miscellaneous Important ───
  ['attention map', 'Attention Map', 'deep learning', ['Visualization', 'Interpretability', 'Transformer', 'Heatmap']],
  ['feature map', 'Feature Map', 'deep learning', ['CNN', 'Convolution', 'Activation Map', 'Filters']],
  ['receptive field', 'Receptive Field', 'deep learning', ['CNN', 'Convolution', 'Kernel Size', 'Depth']],
  ['stride', 'Stride', 'deep learning', ['CNN', 'Convolution', 'Downsampling', 'Padding']],
  ['padding', 'Padding', 'deep learning', ['CNN', 'Same Padding', 'Valid Padding', 'Convolution']],
  ['kernel size', 'Kernel Size', 'deep learning', ['CNN', 'Filter', 'Receptive Field', 'Convolution']],
  ['filter', 'Filter (Kernel)', 'deep learning', ['CNN', 'Convolution', 'Feature Detection', 'Weights']],
  ['channel', 'Channels', 'deep learning', ['RGB', 'Feature Maps', 'CNN', 'Depth']],
  ['latent space', 'Latent Space', 'deep learning', ['VAE', 'Autoencoder', 'Representation', 'Generative']],
  ['encoder decoder', 'Encoder-Decoder', 'deep learning', ['Seq2Seq', 'Autoencoder', 'U-Net', 'Transformer']],
  ['encoder', 'Encoder', 'deep learning', ['Encoder-Decoder', 'BERT', 'Feature Extraction', 'Compression']],
  ['decoder', 'Decoder', 'deep learning', ['Encoder-Decoder', 'GPT', 'Generation', 'Autoregressive']],
  ['teacher forcing', 'Teacher Forcing', 'training', ['Seq2Seq', 'RNN', 'Training', 'Exposure Bias']],
  ['beam search', 'Beam Search', 'inference', ['Decoding', 'NLP', 'Sequence Generation', 'Greedy']],
  ['greedy decoding', 'Greedy Decoding', 'inference', ['Beam Search', 'Sequence Generation', 'NLP']],
  ['temperature', 'Temperature (Sampling)', 'inference', ['Softmax', 'Randomness', 'Generation', 'LLM']],
  ['top-k sampling', 'Top-K Sampling', 'inference', ['Generation', 'LLM', 'Temperature', 'Nucleus']],
  ['nucleus sampling', 'Nucleus (Top-P) Sampling', 'inference', ['Generation', 'Top-K', 'LLM', 'Diversity']],
  ['inference', 'Inference', 'deployment', ['Prediction', 'Deployment', 'Latency', 'TensorRT']],
  ['deployment', 'Model Deployment', 'deployment', ['Inference', 'ONNX', 'API', 'Production']],
  ['gpu', 'GPU Computing', 'hardware', ['CUDA', 'Training', 'NVIDIA', 'Parallelism']],
  ['cuda', 'CUDA', 'hardware', ['GPU', 'NVIDIA', 'Parallel Computing', 'PyTorch']],
  ['tpu', 'TPU', 'hardware', ['Google', 'Training', 'Matrix Operations', 'TensorFlow']],
]

// ── Question Templates (applied dynamically to any topic) ──────
const Q_TEMPLATES = [
  (name) => `What is ${name}?`,
  (name) => `How does ${name} work?`,
  (name) => `Explain ${name}`,
  (name) => `What are the advantages of ${name}?`,
  (name) => `Compare ${name} with alternatives`,
]


export default function SearchPanel({ result, loading, error, onSearch, settings, onViewPdf, activeSource }) {
  const [query, setQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputRef = useRef(null)
  const suggestionsRef = useRef(null)

  // ── Smart autocomplete: match user input against AI_TOPICS and generate questions ──
  const filteredSuggestions = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (q.length < 2) return []

    const results = []
    const seen = new Set()

    // Find all matching topics
    const matchedTopics = AI_TOPICS.filter(([key, name]) =>
      key.includes(q) || name.toLowerCase().includes(q) || q.includes(key)
    )

    // Generate questions from matched topics using templates
    for (const [, name] of matchedTopics) {
      for (const template of Q_TEMPLATES) {
        const question = template(name)
        if (!seen.has(question)) {
          seen.add(question)
          results.push(question)
        }
        if (results.length >= 8) break
      }
      if (results.length >= 8) break
    }

    return results
  }, [query])

  // ── Related topics: detect keywords from current query ──
  const relatedTopics = useMemo(() => {
    if (!query.trim()) return []
    const q = query.toLowerCase()
    const topics = new Set()

    for (const [key, , , related] of AI_TOPICS) {
      if (q.includes(key) || key.includes(q.split(' ')[0])) {
        related.forEach(t => topics.add(t))
      }
    }

    return [...topics].slice(0, 8)
  }, [query])

  // Close suggestions on click outside
  useEffect(() => {
    const handler = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target) && !inputRef.current.contains(e.target)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const doSearch = (text) => {
    if (!text.trim()) return
    setShowSuggestions(false)
    inputRef.current?.blur()
    onSearch({
      query: text.trim(),
      topK: settings.topK,
      model: settings.model,
      bookFilter: settings.bookFilter,
      methods: settings.methods,
    })
  }

  const handleSearch = () => doSearch(query)

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch()
  }

  const selectSuggestion = (s) => {
    setQuery(s)
    doSearch(s)
  }

  const handleRelatedClick = (topic) => {
    const q = `What is ${topic}?`
    setQuery(q)
    doSearch(q)
  }

  // Highlight matching text in suggestion
  const highlightMatch = (text, q) => {
    if (!q.trim()) return text
    const idx = text.toLowerCase().indexOf(q.toLowerCase())
    if (idx === -1) return text
    const before = text.slice(0, idx)
    const match = text.slice(idx, idx + q.length)
    const after = text.slice(idx + q.length)
    return (
      <>
        {before}
        <span className="font-bold text-accent-600">{match}</span>
        {after}
      </>
    )
  }

  const isSearchActive = !!result || loading || !!error;

  return (
    <div className="h-full flex flex-col bg-surface-100 relative overflow-hidden">
      
      {/* Spacer that smoothly pushes the search down when inactive */}
      <div className={`transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] ${isSearchActive ? 'h-0' : 'h-[25vh] min-h-[100px]'}`} />

      {/* The Search Header (hugs content tightly so background adjusts automatically) */}
      <div className={`
        relative z-10 w-full px-6 transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)]
        ${isSearchActive 
          ? 'pt-6 pb-5 bg-white border-b border-neutral-100 shadow-soft' 
          : 'pt-0 pb-0 bg-transparent border-transparent'}
      `}>
        <div className={`mx-auto transition-all duration-700 w-full flex flex-col ${isSearchActive ? 'max-w-full items-start' : 'max-w-3xl items-center text-center'}`}>
          
          <h2 className={`font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-accent-600 to-accent-400 transition-all duration-700 pb-1 ${isSearchActive ? 'text-xl mb-0.5' : 'text-[2.75rem] leading-tight mb-3 tracking-tight'}`}>
            {isSearchActive ? 'Ask a Question' : 'AI Textbook Q&A'}
          </h2>
          <p className={`text-neutral-400 transition-all duration-700 ${isSearchActive ? 'text-xs mb-4' : 'text-[15px] mb-10 tracking-wide'}`}>
            Search across 46 AI/ML textbooks with source tracing
          </p>

          <div className={`flex gap-3 w-full transition-all duration-700 ${isSearchActive ? 'scale-100' : 'scale-[1.02]'}`}>
            <div className={`flex-1 relative transition-all duration-700 ${isSearchActive ? 'shadow-none' : 'shadow-lg hover:shadow-xl rounded-2xl'}`}>
              
              {/* Left Search Icon */}
              <svg
                className={`absolute top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none transition-all duration-700 ${isSearchActive ? 'w-4 h-4 left-3.5' : 'w-5 h-5 left-5 text-accent-400/70'}`}
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>

              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={e => { setQuery(e.target.value); setShowSuggestions(true) }}
                onFocus={() => setShowSuggestions(true)}
                onKeyDown={handleKeyDown}
                placeholder="e.g. What is the transformer attention mechanism?"
                className={`w-full bg-white border-2 text-neutral-700 placeholder:text-neutral-400 focus:outline-none focus:border-accent-500 focus:ring-4 focus:ring-accent-500/15 transition-all duration-700
                  ${isSearchActive 
                    ? 'pl-10 pr-4 py-2.5 rounded-xl border-neutral-200 text-sm' 
                    : 'pl-14 pr-6 py-4 rounded-2xl border-transparent focus:border-accent-500 hover:border-neutral-200 text-base'
                  }`}
              />

              {/* Autocomplete dropdown */}
              {showSuggestions && filteredSuggestions.length > 0 && (
                <div ref={suggestionsRef}
                  className={`absolute left-0 right-0 mt-2 bg-white border border-neutral-200 shadow-xl z-20 overflow-hidden animate-fade-in ${isSearchActive ? 'rounded-xl top-full' : 'rounded-2xl top-full'}`}>
                  {filteredSuggestions.map((s, i) => (
                    <button key={i} onClick={() => selectSuggestion(s)}
                      className="w-full px-5 py-3 text-left text-[15px] text-neutral-600 hover:bg-neutral-50 hover:text-accent-600 transition-colors flex items-center gap-3">
                      <svg className="w-4 h-4 text-neutral-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <span>{highlightMatch(s, query)}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className={`btn-primary font-bold active:scale-[0.98] transition-all duration-700 shadow-sm flex items-center justify-center
                ${isSearchActive ? 'px-6 py-2.5 text-sm rounded-xl' : 'px-8 py-3 text-base shadow-md hover:shadow-lg rounded-2xl'}`}
            >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="spinner" />
                <span>Searching…</span>
              </div>
            ) : 'Search'}
          </button>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className={`flex-1 relative z-0 overflow-y-auto px-6 py-4 space-y-4 transition-all duration-700 ease-[cubic-bezier(0.25,1,0.5,1)] scrollbar-thin
        ${isSearchActive ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12 pointer-events-none absolute left-0 right-0'}`}>
        
        {/* Prominent Center Loading State */}
        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center z-10 bg-white animate-fade-in">
            <div className="w-16 h-16 relative flex items-center justify-center mb-6">
              <div className="absolute inset-0 rounded-full border-4 border-accent-100 opacity-20"></div>
              <div className="absolute inset-0 rounded-full border-4 border-accent-600 border-t-transparent animate-spin"></div>
              <div className="absolute inset-2 rounded-full border-4 border-accent-400 border-b-transparent animate-spin-slow opacity-80"></div>
              <svg className="w-5 h-5 text-accent-600 absolute" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <p className="text-base font-bold text-neutral-800 tracking-tight">Searching Textbooks...</p>
            <p className="text-xs text-neutral-400 mt-2">Retrieving and reading relevant sources</p>
          </div>
        )}

        {/* Related Topics Chips — shown after search completes */}
        {!loading && result && relatedTopics.length > 0 && (
          <div className="animate-fade-in">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mr-1">Related</span>
              {relatedTopics.map((topic, i) => (
                <button
                  key={i}
                  onClick={() => handleRelatedClick(topic)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                    bg-accent-50 text-accent-700 border border-accent-100
                    hover:bg-accent-100 hover:border-accent-200 hover:text-accent-800 hover:shadow-sm
                    active:scale-95 transition-all duration-200"
                >
                  <svg className="w-3 h-3 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  {topic}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="p-3.5 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm animate-fade-in">
            {error}
          </div>
        )}

        {/* Answer */}
        {!loading && result?.answer && (
          <div className="animate-slide-up">
            <h3 className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-2">Answer</h3>
            <div className="answer-box px-5 py-4 rounded-r-xl bg-white shadow-soft">
              <div className="text-sm text-neutral-700 leading-relaxed whitespace-pre-wrap">
                {result.answer}
              </div>
            </div>
          </div>
        )}

        {/* Sources */}
        {!loading && result?.sources?.length > 0 && (() => {
          // Group sources by book_id
          const groupedSources = []
          const map = new Map()
          result.sources.forEach(src => {
            if (!map.has(src.book_id)) {
              map.set(src.book_id, { book_id: src.book_id, items: [] })
              groupedSources.push(map.get(src.book_id)) // preserve ranking order
            }
            map.get(src.book_id).items.push(src)
          })
          
          // Sort items within each book by score descending
          groupedSources.forEach(group => {
            group.items.sort((a, b) => (b.score || 0) - (a.score || 0))
          })

          return (
            <div className="animate-slide-up" style={{ animationDelay: '80ms' }}>
              <h3 className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-2">
                Source Books ({groupedSources.length})
              </h3>
              <div className="space-y-2">
                {groupedSources.map((group, i) => (
                  <SourceCard
                    key={group.book_id}
                    group={group}
                    index={i}
                    onViewPdf={onViewPdf}
                    activeChunkId={activeSource?.chunk_id}
                  />
                ))}
              </div>
            </div>
          )
        })()}
      </div>
    </div>
  )
}
