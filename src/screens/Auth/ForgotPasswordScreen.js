import { LinearGradient } from 'expo-linear-gradient';
import { useState } from 'react';
import { Alert, Image, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function ForgotPasswordScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePasswordReset = async () => {
    if (!email) {
      Alert.alert("Aviso", "Digite o seu e-mail cadastrado.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/password-reset/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({ email: email })
      });

      if (response.ok) {
        Alert.alert("Sucesso", "Instruções de recuperação enviadas para o seu e-mail.");
        navigation.goBack();
      } else {
        Alert.alert("Erro", "E-mail não encontrado ou inválido.");
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient colors={['#3AC0ED', '#72FC90']} style={styles.headerGradient}>
        <Image source={require('../../../assets/images/react-logo.png')} style={styles.logo} />
        <Text style={styles.title}>VigiAA</Text>
        <Text style={styles.subtitle}>Recuperar Senha</Text>
      </LinearGradient>

      <View style={styles.formContainer}>
        <Text style={styles.instructionText}>
          Insira o e-mail associado à sua conta para receber as instruções de redefinição de senha.
        </Text>

        <TextInput
          style={styles.input}
          placeholder="E-mail"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <TouchableOpacity style={styles.button} onPress={handlePasswordReset} disabled={loading}>
          <Text style={styles.buttonText}>{loading ? "Enviando..." : "Enviar Instruções"}</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backLinkContainer}>
          <Text style={styles.backLinkText}>Voltar para o Login</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  headerGradient: {
    height: '35%',
    borderBottomLeftRadius: 60,
    borderBottomRightRadius: 60,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: { width: 80, height: 80, marginBottom: 5, resizeMode: 'contain' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#000' },
  subtitle: { fontSize: 15, fontWeight: '600', color: '#000' },
  formContainer: { padding: 25, marginTop: 10 },
  instructionText: { fontSize: 14, color: '#666', textAlign: 'center', marginBottom: 20, lineHeight: 20 },
  input: {
    borderWidth: 1,
    borderColor: '#CCC',
    borderRadius: 12,
    height: 50,
    paddingHorizontal: 15,
    marginBottom: 15,
    backgroundColor: '#FAFAFA',
    color: '#000',
  },
  button: {
    backgroundColor: '#000',
    height: 50,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 5,
  },
  buttonText: { color: '#FFF', fontWeight: 'bold', fontSize: 16 },
  backLinkContainer: { marginTop: 20, alignItems: 'center' },
  backLinkText: { color: '#1D76D2', fontWeight: 'bold' },
});