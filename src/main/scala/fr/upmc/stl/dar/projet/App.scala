package fr.upmc.stl.dar.projet

import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.classification.{RandomForestClassificationModel, RandomForestClassifier}
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql._
import org.apache.spark.ml.feature._

object App {

  val ROOT_PATH: String = "/home/thibault/Documents/FAC/Master/Master_2/DAR/StackOverflowML/"
  val filename: String = "dataset.json"

  def main (arg: Array[String]): Unit = {

    val conf = new SparkConf().setAppName("StackOverflowML").setMaster("local")
    val sc = new SparkContext(conf)
    val sparkSession = SparkSession.builder
      .master("local")
      .appName("StackOverflowML")
      .getOrCreate()

    import sparkSession.sqlContext.implicits._
    val sqlContext = sparkSession.sqlContext

    val dataFrame = sqlContext.read.option("multiline", "true").json("test.json").toDF()
    dataFrame.show()

    val columns: Array[String] = dataFrame.columns
    val reorderedColumnNames: Array[String] = Array("id","title","text","code","tags") // do the reordering you want
    val orderedDF: DataFrame = dataFrame.select(reorderedColumnNames.head, reorderedColumnNames.tail: _*)

    val wordsListClean = orderedDF.select("text")
      .map(row => cleanWords(row.getString(0).split(" ")))
    wordsListClean.show()

    val tokenizerText = new Tokenizer().setInputCol("value").setOutputCol("words")
    val wordsData = tokenizerText.transform(wordsListClean)
    wordsData.show()
    wordsData.printSchema()


    /*TF IDF over cleaned datas*/
    val hashingTF = new HashingTF().setInputCol("words").setOutputCol("rawFeatures").setNumFeatures(50000)
    val featurizedWords = hashingTF.transform(wordsData)
    featurizedWords.show()

    val idf = new IDF().setInputCol("rawFeatures").setOutputCol("features")
    val idfModel = idf.fit(featurizedWords)

    val rescaledWords = idfModel.transform(featurizedWords)
    val datas = rescaledWords.select("words","features")
    datas.show()

    val wordsIndexer = new StringIndexer().setInputCol("value").setOutputCol("indexedWords")
      .fit(featurizedWords)
    val res = wordsIndexer.transform(rescaledWords).toDF("label","words","rawFeatures","features","indexedWords")
    res.show()
    res.printSchema()

    /*val labeledPoints = res.map(
      row => {
        val vector = row.getAs[Vector](3)
        val id = row.getAs[Double](4)
        LabeledPoint(id,vector)
      }
    )*/

    val wordsIndexer2 = new StringIndexer()
      .setInputCol("label")
      .setOutputCol("indexedLabel")
      .fit(res)

    val featureIndexer = new VectorIndexer()
      .setInputCol("features")
      .setOutputCol("indexedFeatures")
      .setMaxCategories(4)
      .fit(res)

    val Array(trainingData,testData) = res.randomSplit(Array(0.7,0.3), seed = 1234L)

    // Train a RandomForest model.
    val rf = new RandomForestClassifier()
      .setLabelCol("indexedLabel")
      .setFeaturesCol("indexedFeatures")
      .setNumTrees(10)

    // Convert indexed labels back to original labels.
    val labelConverter = new IndexToString()
      .setInputCol("prediction")
      .setOutputCol("predictedLabel")
      .setLabels(wordsIndexer.labels)

    // Chain indexers and forest in a Pipeline.
    val pipeline = new Pipeline()
      .setStages(Array(wordsIndexer2, featureIndexer, rf, labelConverter))

    // Train model. This also runs the indexers.
    val model = pipeline.fit(trainingData)

    // Make predictions.
    val predictions = model.transform(testData)

    // Select example rows to display.
    predictions.select("predictedLabel", "label", "features").show(5)

    // Select (prediction, true label) and compute test error.
    val evaluator = new MulticlassClassificationEvaluator()
      .setLabelCol("indexedLabel")
      .setPredictionCol("prediction")
      .setMetricName("accuracy")
    val accuracy = evaluator.evaluate(predictions)
    println("Test Error = " + (1.0 - accuracy))

    val rfModel = model.stages(2).asInstanceOf[RandomForestClassificationModel]
    println("Learned classification forest model:\n" + rfModel.toDebugString)

  }

  def cleanWords (words: Array[String]): String = {
    val stopwords_list = Array(
      "a",  "about",  "above",  "after",  "again",  "against",  "all",  "am",  "an",  "and",  "any",  "are",  "arent",  "as",  "at",
     "be",  "because",  "been",  "before",  "being",  "below",  "between",  "both",  "but",  "by",
     "can", "cant", "come",  "could", "couldnt",
     "d",  "did",  "didn",  "do",  "does",  "doesnt",  "doing",  "dont",  "down",  "during",
     "each",
     "few", "finally",  "for",  "from",  "further",
     "had",  "hadnt",  "has",  "hasnt",  "have",  "havent",  "having",  "he",  "her",  "here",  "hers",  "herself",  "him",  "himself",  "his",  "how",
     "i",  "if",  "in",  "into",  "is",  "isnt",  "it",  "its",  "itself",
     "just",
     "ll",
     "m",  "me",  "might",  "more",  "most",  "must",  "my",  "myself",
     "no",  "nor",  "not",  "now",
     "o",  "of",  "off",  "on",  "once",  "only",  "or",  "other",  "our",  "ours",  "ourselves",  "out",  "over",  "own",
     "r",  "re",
     "s", "said",  "same",  "she",  "should",  "shouldnt",  "so",  "some",  "such", "still",
     "t",  "than",  "that", "thats",  "the",  "their",  "theirs",  "them",  "themselves",  "then",  "there",  "these",  "they",  "this",  "those",  "through",  "to",  "too",
     "under",  "until",  "up",
     "very",
     "was",  "wasnt",  "we",  "were",  "werent",  "what",  "when",  "where",  "which",  "while",  "who",  "whom",  "why",  "will",  "with",  "wont",  "would",
     "y",  "yo ",  "your",  "yours",  "yourself",  "yourselves")
    val stopwords_list_custom = Array("try","trying","need","know", "following")
    val stopwords = stopwords_list ++ stopwords_list_custom


    val res = words.filterNot(_.isEmpty).filter(word =>
      word.toLowerCase.length>2 && !stopwords.contains(word.toLowerCase) && word.matches("[A-Za-z]+"))
    res.mkString(" ")
  }

}
