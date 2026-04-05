import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'pages/login_page.dart';
import 'pages/home_page.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const CadastroEficienteApp());
}

class CadastroEficienteApp extends StatelessWidget {
  const CadastroEficienteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cadastro Eficiente',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0B1F3A),
        ),
        useMaterial3: true,
      ),
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool carregando = true;
  String? username;
  String? nomeExibicao;

  @override
  void initState() {
    super.initState();
    verificarSessao();
  }

  Future<void> verificarSessao() async {
    final prefs = await SharedPreferences.getInstance();
    username = prefs.getString('username');
    nomeExibicao = prefs.getString('nome_exibicao');

    setState(() {
      carregando = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (carregando) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (username != null && nomeExibicao != null) {
      return HomePage(
        username: username!,
        nomeExibicao: nomeExibicao!,
      );
    }

    return const LoginPage();
  }
}