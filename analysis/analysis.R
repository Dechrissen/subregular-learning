library(PMCMRplus) # provides frdAllPairsNemenyiTest()
library(reshape2)  # provides acast()
library(dplyr)     # provides recode_factor
library(ggplot2)   # provides ggplot
library(effsize)   # provides cohen.d

# DATA PREPARATION
cols = c("alph", "tier", "class", "k", "j", "i", "network_type",
         "train_set_size", "test_type", "accuracy", "fscore", "auc", "brier")
eval = read.csv('all_evals.csv', header=TRUE)[cols]

# removing the experiments involving size 64 alph languages because data is bad
eval <- filter(eval, alph != 64)

eval$alph = as.factor(eval$alph)
eval$tier = as.factor(eval$tier)
eval$class = as.factor(eval$class)
eval$network_type = as.factor(eval$network_type)
eval$train_set_size = as.factor(eval$train_set_size)
eval$test_type = as.factor(eval$test_type)

cnts = read.table('counts.tsv', header=TRUE, sep='\t')
data = merge(
     eval,
     cnts,
     by.x=c("alph", "tier", "class", "k", "j", "i"),
     by.y=c("Alph", "Tier", "Class", "k", "j", "i")
)

data$network_type = recode_factor(data$network_type,
                                  simple="Simple RNN",
                                  gru="GRU",
                                  lstm="LSTM",
                                  stackedrnn="2-layer LSTM",
                                  transformer="Transformer")



# SET UP CAST MATRIX WITH LANG CLASSES AS COLUMNS
df = aggregate(data$accuracy,
               by=list(alph=data$alph,
                       network_type=data$network_type,
                       train_set_size=data$train_set_size,
                       test_type=data$test_type,
                       class=data$class),
               FUN=mean)
cast.matrix = acast(df,
                    alph + network_type + train_set_size + test_type ~ class,
                    value.var="x")
cast.df = as.data.frame(cast.matrix)


# SANITY CHECK:
# ========================================================================
# DOES NN ACCURACY INCREASE WITH TRAIN SET SIZE?
data.matrix = acast(df,
                    alph + class + network_type + test_type ~ train_set_size,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL SIZES HAVE THE SAME ACCURACY.

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# TRAIN SET SIZES ARE DIFFERENT IN THE EXPECTED WAY.
# ========================================================================


# TEST TYPE DIFFICULTY IS AS FOLLOWS: SR < LR < SA < LA
# ========================================================================


# FRIEDMAN TEST FOR LANGUAGE CLASSES
# ========================================================================
friedman.test(cast.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL LG CLASSES HAVE THE SAME ACCURACY.

frdAllPairsNemenyiTest(cast.matrix)
colMeans(cast.matrix)

# SANITY CHECK : SL/coSL, SP/coSP, TSL/TcoSL all-pairs p-values are close to 1.


# ========================================================================
# FRIEDMAN TEST FOR TEST TYPES
# ========================================================================
# DOES NN ACCURACY DECREASE ACROSS THE TEST TYPES SR < (SA <> LR) < LA?
data.matrix = acast(df,
                    alph + class + network_type + train_set_size ~ test_type,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL SIZES HAVE THE SAME ACCURACY.

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)

# ========================================================================
# COHEN'S D FOR TEST TYPES
# ========================================================================
sa <- subset(eval, eval$test_type == 'SA')
sr <- subset(eval, eval$test_type == 'SR')
la <- subset(eval, eval$test_type == 'LA')
lr <- subset(eval, eval$test_type == 'LR')
cohen.d(sr$accuracy, lr$accuracy) #$estimate
cohen.d(lr$accuracy, sa$accuracy) #$estimate
cohen.d(sa$accuracy, la$accuracy) #$estimate


# ========================================================================
# DIFFERENCES BETWEEN CNL, DPL, PROP, FO, REG
# ========================================================================

cnl = c("SL", "SP", "TSL")
dpl = c("coSL", "coSP", "TcoSL")
prop = c("LT", "PLT", "PT", "TLT", "TPLT")
fo = c("LTT", "TLTT", "SF")
reg = c("Zp", "Reg")
data$logic <-
     ifelse(data$class %in% cnl, "CNL",
     ifelse(data$class %in% dpl, "DPL",
     ifelse(data$class %in% prop, "PROP",
     ifelse(data$class %in% fo, "FO",
     ifelse(data$class %in% reg, "REG", "OTHER")))))

logic.agg = aggregate(data$accuracy,
                      by=list(alph=data$alph,
                              network_type=data$network_type,
                              train_set_size=data$train_set_size,
                              test_type=data$test_type,
                              logic=data$logic),
                      FUN=mean)
data.matrix = acast(logic.agg,
                    alph + network_type + train_set_size + test_type ~ logic,
                    value.var="x")

friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL LOGICS ARE THE SAME

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# REG IS HARDEST TO LEARN. OTHERS ARE NOT SO CLEAR.
# ========================================================================

# ========================================================================
# COHEN'S D FOR LOGICAL LEVELS
# ========================================================================
cnl  <- subset(data, data$logic == "CNL")
dpl  <- subset(data, data$logic == "DPL")
prop <- subset(data, data$logic == "PROP")
fo   <- subset(data, data$logic == "FO")
reg  <- subset(data, data$logic == "REG")

cohen.d(cnl$accuracy, dpl$accuracy) #$estimate
cohen.d(cnl$accuracy, prop$accuracy)
cohen.d(cnl$accuracy, fo$accuracy)
cohen.d(cnl$accuracy, reg$accuracy)
cohen.d(dpl$accuracy, prop$accuracy)
cohen.d(dpl$accuracy, fo$accuracy)
cohen.d(dpl$accuracy, reg$accuracy)
cohen.d(prop$accuracy, fo$accuracy)
cohen.d(prop$accuracy, reg$accuracy)
cohen.d(fo$accuracy, reg$accuracy)






# ========================================================================
# DIFFERENCES BETWEEN PROPOSITIONAL LOGICS BY ORDER RELATION
# ========================================================================
succ = c("SL", "coSL", "LT", "LTT")
prec = c("coSP", "PT", "SF", "SP")
tsucc = c("TcoSL", "TLT", "TLTT", "TSL")
data$prop <-
  ifelse(data$class %in% succ, "SUCC",
         ifelse(data$class %in% prec, "PREC",
                ifelse(data$class %in% tsucc, "TSUCC", "OTHER")))

prop.agg = aggregate(data$accuracy,
                     by=list(alph=data$alph,
                             network_type=data$network_type,
                             train_set_size=data$train_set_size,
                             test_type=data$test_type,
                             prop=data$prop),
                     FUN=mean)
data.matrix = acast(prop.agg,
                    alph + network_type + train_set_size + test_type ~ prop,
                    value.var="x")

friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p = 2.244e-08 --> NOT ALL LOGICS ARE THE SAME

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# PRECEDENCE IS HARDER TO LEARN THAN SUCCESSOR
# TSUCC & SUCC THE SAME
# ========================================================================


# ========================================================================
# COHEN'S D FOR ORDERING RELATION
# ========================================================================
succ <- subset(data, data$prop == "SUCC")
prec  <- subset(data, data$prop == "PREC")
tsucc <- subset(data, data$prop == "TSUCC")
other   <- subset(data, data$prop == "OTHER")

cohen.d(succ$accuracy, prec$accuracy) #$estimate
cohen.d(succ$accuracy, tsucc$accuracy)
cohen.d(succ$accuracy, other$accuracy)
cohen.d(prec$accuracy, tsucc$accuracy)
cohen.d(prec$accuracy, other$accuracy)
cohen.d(tsucc$accuracy, other$accuracy)

# ========================================================================
# FRIEDMAN TEST FOR ALPHABET SIZES:
# ========================================================================
data.matrix = acast(df,
                    class + network_type + train_set_size + test_type ~ alph,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL ALPHABETS HAVE SAME ACCURACY.

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# DIFFICULTY NEARLY IN ASCENDING ORDER: 64 --> 16, 4
# ========================================================================

# ========================================================================
# COHEN'S D FOR ALPHABET SIZES
# ========================================================================
a64 <- subset(data, data$alph == 64)
a16 <- subset(data, data$alph == 16)
a04 <- subset(data, data$alph == 4)

cohen.d(a64$accuracy, a16$accuracy) #$estimate
cohen.d(a64$accuracy, a04$accuracy)
cohen.d(a16$accuracy, a04$accuracy)


# ========================================================================
# FRIEDMAN TEST FOR NETWORK TYPES
# ========================================================================
# ALL Training Sets
data.matrix = acast(df,
                    alph + class + train_set_size + test_type ~ network_type,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL NNs HAVE THE SAME ACCURACY.

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# SIMPLE RNNs OUTPERFORM GRUs, LSTMs, AND TRANSFORMERS
# NO SIGNIFICANT DIFFERENCE BETWEEN SIMPLE AND 2layer LSTM
# ========================================================================

# ========================================================================
# COHEN'S D FOR NETWORK TYPE
# ========================================================================
srnn  <- subset(data, data$network_type == "Simple RNN")
lstm  <- subset(data, data$network_type == "LSTM")
gru   <- subset(data, data$network_type == "GRU")
lstm2 <- subset(data, data$network_type == "2-layer LSTM")
tran  <- subset(data, data$network_type == "Transformer")

cohen.d(srnn$accuracy, lstm2$accuracy) #$estimate
cohen.d(lstm2$accuracy, lstm$accuracy)
cohen.d(lstm$accuracy, gru$accuracy)
cohen.d(gru$accuracy, tran$accuracy)

cohen.d(srnn$accuracy, gru$accuracy)

# Small Training Set
# ==================
df.temp = df[df$train_set_size == "Small",]
data.matrix = acast(df.temp,
                    alph + class + train_set_size + test_type ~ network_type,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 
# --> NOT ALL NNs HAVE THE SAME ACCURACY ON SMALL TRAINING DATA

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# SIMPLE RNNS OUTPERFORM EVERYTHING
# NO SIGNIFICANT DIFFERENCES AMONG OTHERS
# ========================================================================

# ========================================================================
# COHEN'S D FOR NETWORK TYPE (SMALL)
# ========================================================================
srnn  <- subset(data, data$network_type == "Simple RNN" & data$train_set_size=="Small")
lstm  <- subset(data, data$network_type == "LSTM" & data$train_set_size=="Small")

cohen.d(srnn$accuracy, lstm$accuracy) #$estimate




# Mid Training Set
df.temp = df[df$train_set_size == "Mid",]
data.matrix = acast(df.temp,
                    alph + class + train_set_size + test_type ~ network_type,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 
# --> NOT ALL NNs HAVE THE SAME ACCURACY ON MID TRAINING DATA

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# SIMPLE, LSTM, 2LSTM ARE NOT SIGNIFICANTLY DIFFERENT FROM EACH OTHER
# SIMPLE, LSTM, 2LSTM ARE SIGNIFICANTLY DIFFERENT FROM GRU, TRANSFORMER
# ========================================================================

# ========================================================================
# COHEN'S D FOR NETWORK TYPE (MID)
# ========================================================================
gru  <- subset(data, data$network_type == "GRU" & data$train_set_size=="Mid")
lstm  <- subset(data, data$network_type == "LSTM" & data$train_set_size=="Mid")
tran  <- subset(data, data$network_type == "Transformer" & data$train_set_size=="Mid")
lstm2  <- subset(data, data$network_type == "2-layer LSTM" & data$train_set_size=="Mid")

cohen.d(gru$accuracy, lstm$accuracy) #$estimate
cohen.d(gru$accuracy, tran$accuracy) #$estimate
cohen.d(lstm2$accuracy, lstm$accuracy) #$estimate
cohen.d(lstm2$accuracy, tran$accuracy) #$estimate

# Large Training Set
df.temp = df[df$train_set_size == "Large",]
data.matrix = acast(df.temp,
                    alph + class + train_set_size + test_type ~ network_type,
                    value.var="x")
friedman.test(data.matrix)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL NNs HAVE THE SAME ACCURACY.

# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.matrix)
colMeans(data.matrix)
# 2LSTM SIGNIFICANTLY DIFFERENT THAN ALL OTHERS
# ========================================================================

# ========================================================================
# COHEN'S D FOR NETWORK TYPE (LARGE)
# ========================================================================
srnn  <- subset(data, data$network_type == "Simple RNN" & data$train_set_size=="Large")
lstm  <- subset(data, data$network_type == "LSTM" & data$train_set_size=="Large")
tran  <- subset(data, data$network_type == "Transformer" & data$train_set_size=="Large")
lstm2  <- subset(data, data$network_type == "2-layer LSTM" & data$train_set_size=="Large")

cohen.d(lstm2$accuracy, lstm$accuracy) #$estimate
cohen.d(lstm2$accuracy, tran$accuracy) #$estimate
cohen.d(lstm2$accuracy, srnn$accuracy) #$estimate



# DO k VALUES MAKE A DIFFERENCE FOR PROP1 AND PROP2?
# ========================================================================
succ = c("SL", "coSL", "LT", "LTT")
prec = c("coSP", "PT", "SP") # removed SF
tsucc = c("TcoSL", "TLT", "TLTT", "TSL")

prop1 = c(succ, prec, tsucc)
prop2 = prop1[!(prop1 %in% c("LTT", "TLTT"))]

df.temp = aggregate(data$accuracy,
                    by=list(alph=data$alph,
                            class=data$class,
                            k=data$k,
                            network_type=data$network_type,
                            train_set_size=data$train_set_size,
                            test_type=data$test_type),
                    FUN=mean)

df.temp1 = df.temp[df.temp$class %in% prop1,]
data.prop1 = acast(df.temp1,
                   alph + class + network_type + train_set_size + test_type ~ k,
                   value.var="x")
df.temp2 = df.temp[df.temp$class %in% prop2,]
data.prop2 = acast(df.temp2,
                   alph + class + network_type + train_set_size + test_type ~ k,
                   value.var="x")

friedman.test(data.prop1)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL k VALS HAVE SAME ACCURACY.
# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.prop1)
colMeans(data.prop1)
# FOR PROP1, k=2 SIGNIFICANTLY EASIER THAN k=4,6 BUT k=4 NOT SIGNIFICANTLY
# DIFFERENT THAN k=6

friedman.test(data.prop2)
# FRIEDMAN REJECTED AT p < 2.2e-16 --> NOT ALL k VALS HAVE SAME ACCURACY.
# POST HOC MULTIPLE COMPARISONS ANALYSIS
frdAllPairsNemenyiTest(data.prop2)
colMeans(data.prop2)
# FOR PROP2, k=2 SIGNIFICANTLY EASIER THAN k=4,6 BUT k=4 NOT SIGNIFICANTLY
# DIFFERENT THAN k=6
# ========================================================================



# ========================================================================
# VISUALIZATIONS
# ========================================================================

lang.order = c("SL", "coSL", "TSL", "TcoSL", "SP", "coSP", "LT", "TLT",
               "PT", "LTT", "TLTT", "PLT", "TPLT", "SF", "Zp", "Reg")
size.order = c("Small", "Mid", "Large")
test.order = c("SR", "LR", "SA", "LA")
nn.order = c("Simple RNN", "GRU", "LSTM", "2-layer LSTM", "Transformer")
drc.order = c("1Q", "2Q", "3Q", "4Q")

( # VISUALIZE CAST.DF, i.e. CLASS ACCURACY AGGREGATED OVER TIER, k, j, i
  ggplot(stack(cast.df), aes(x=ind, y=values))
  + geom_boxplot()
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy")
)

jpeg("acc_class_alph.jpeg", units="in", width=10, height=5, res=300)
(
  ggplot(data, aes(x=class, y=accuracy, fill=alph))
  + geom_boxplot(outlier.shape=NA)
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class and Alphabet Size")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy", fill="Alphabet Size")
)
dev.off()

jpeg("acc_k_alph.jpeg", units="in", width=10, height=5, res=300)
( # ACCURACY BY k VALUES
  ggplot(data, aes(x=factor(k), y=accuracy, fill=alph))
  + geom_boxplot(outlier.shape=NA)
  + ggtitle("Accuracy by k Values and Alphabet Size")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="k Values", y="Accuracy", fill="Alphabet Size")
)
dev.off()

jpeg("acc_class_trainsize.jpeg", units="in", width=10, height=5, res=300)
(
  ggplot(data, aes(x=class, y=accuracy, fill=factor(train_set_size, levels=size.order)))
  + geom_boxplot(outlier.shape=NA)
  + scale_fill_discrete(limits=size.order)
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class and Training Set Size")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy", fill="Training Set Size")
)
dev.off()

jpeg("acc_class_test.jpeg", units="in", width=10, height=5, res=300)
(
  ggplot(data, aes(x=class, y=accuracy, fill=factor(test_type, levels=test.order)))
  + geom_boxplot(outlier.shape=NA)
  + scale_fill_discrete(limits=test.order)
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class and Test Type")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy", fill="Test Type")
)
dev.off()

jpeg("acc_class_test_large.jpeg", units="in", width=10, height=5, res=300)
(
  ggplot(data[data$train_set_size=="Large",], aes(x=class, y=accuracy, fill=factor(test_type, levels=test.order)))
  + geom_boxplot(outlier.shape=NA)
  + scale_fill_discrete(limits=test.order)
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class and Test Type")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy", fill="Test Type")
)
dev.off()


jpeg("acc_class_nn.jpeg", units="in", width=12, height=5, res=300)
(
  ggplot(data, aes(x=class, y=accuracy, fill=factor(network_type, levels=nn.order)))
  + geom_boxplot(outlier.shape=NA)
  + scale_fill_discrete(limits=nn.order)
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class and Network Type")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy", fill="Network Type")
)
dev.off()

jpeg("acc_class_nn_large.jpeg", units="in", width=12, height=5, res=300)
(
  ggplot(data[data$train_set_size=="Large",], aes(x=class, y=accuracy, fill=factor(network_type, levels=nn.order)))
  + geom_boxplot(outlier.shape=NA)
  + scale_fill_discrete(limits=nn.order)
  + scale_x_discrete(limits=lang.order)
  + ggtitle("Accuracy by Class and Network Type (Large Train Set Size)")
  + theme(plot.title=element_text(hjust=0.5))
  + labs(x="Language Class", y="Accuracy", fill="Network Type")
)
dev.off()

#jpeg("acc_class_dratioclass.jpeg", units="in", width=10, height=5, res=300)
#(
#  ggplot(data, aes(x=class, y=accuracy, fill=factor(d.ratio.class, levels=drc.order)))
#  + geom_boxplot(outlier.shape=NA)
#  + scale_x_discrete(limits=lang.order)
#  + ggtitle("Accuracy by Class and D-Ratio Quartile")
#  + theme(plot.title=element_text(hjust=0.5))
#  + labs(x="Language Class", y="Accuracy", fill="D-Ratio Quartile")
#)
#dev.off()
# ========================================================================



#
# EXTRAS
#

# CREATE AGGREGATE MATRIX FOR NNs VS LANGUAGE CLASSES
df.tmp = data[data$train_set_size == "Large",]
agg.tmp = aggregate(df.tmp$accuracy,
                    by=list(network_type=df.tmp$network_type,
                            class=df.tmp$class),
                    FUN=mean)
agg = acast(agg.tmp, network_type ~ class, value.var="x")
agg
# NOTE: TRANSFORMERS OUTPERFORM OTHER NNs ON Zp LANGS FOR LARGE TRAIN SETS

