import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'dashboard_page.dart';
import 'cadastro_page.dart';
import 'login_page.dart';

class HomePage extends StatefulWidget {
  final String username;
  final String nomeExibicao;

  const HomePage({
    super.key,
    required this.username,
    required this.nomeExibicao,
  });

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int indiceAtual = 0;

  Future<void> sair() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginPage()),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final paginas = [
      DashboardPage(
        username: widget.username,
        nomeExibicao: widget.nomeExibicao,
      ),
      CadastroPage(
        username: widget.username,
        nomeExibicao: widget.nomeExibicao,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text('Olá, ${widget.nomeExibicao}'),
        actions: [
          IconButton(
            onPressed: sair,
            icon: const Icon(Icons.logout),
          )
        ],
      ),
      body: paginas[indiceAtual],
      bottomNavigationBar: NavigationBar(
        selectedIndex: indiceAtual,
        onDestinationSelected: (index) {
          setState(() => indiceAtual = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_location_alt),
            label: 'Cadastro',
          ),
        ],
      ),
    );
  }
}