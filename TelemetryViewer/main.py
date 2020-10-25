import Loader


if __name__ == "__main__":
    app = Loader.QApplication(Loader.sys.argv)
    window = Loader.SplashScreen()
    Loader.sys.exit(app.exec_())